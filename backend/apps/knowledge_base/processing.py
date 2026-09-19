"""
Orkestrasi pipeline pemrosesan Knowledge Base (bagian 9): ekstraksi -> chunk
-> embedding -> simpan. Dijalankan sinkron (tidak ada Celery/queue - bagian 2/35).
"""
from django.db import transaction

from apps.knowledge_base.models import KbChunk, KnowledgeBase, ProcessingStatus
from apps.knowledge_base.services.chunking import split_into_chunks
from apps.knowledge_base.services.embedding import embed_texts
from apps.knowledge_base.services.extraction import ExtractionError, extract_text


def process_knowledge_base(kb: KnowledgeBase) -> KnowledgeBase:
    kb.processing_status = ProcessingStatus.PROCESSING
    kb.processing_error = ""
    kb.save(update_fields=["processing_status", "processing_error"])

    try:
        if kb.sumber == "text":
            teks = kb.teks
            butuh_ocr = False
        else:
            teks, butuh_ocr = extract_text(kb.file, kb.sumber)
            kb.teks = teks

        if butuh_ocr:
            kb.processing_status = ProcessingStatus.NEEDS_OCR
            kb.processing_error = "PDF hasil scan -- tidak ada teks yang dapat diekstrak. Membutuhkan OCR."
            kb.save(update_fields=["teks", "processing_status", "processing_error"])
            return kb

        chunk_texts = split_into_chunks(teks)
        if not chunk_texts:
            kb.processing_status = ProcessingStatus.FAILED
            kb.processing_error = "Tidak ada teks yang bisa diproses menjadi chunk."
            kb.save(update_fields=["processing_status", "processing_error"])
            return kb

        embeddings = embed_texts(chunk_texts)

        with transaction.atomic():
            kb.chunks.all().delete()  # rebuild bersih jika materi diperbarui (bagian 9)
            KbChunk.objects.bulk_create(
                [
                    KbChunk(
                        knowledge_base=kb,
                        chunk_index=i,
                        content=content,
                        embedding=embedding,
                        metadata={},
                    )
                    for i, (content, embedding) in enumerate(zip(chunk_texts, embeddings))
                ]
            )
            kb.processing_status = ProcessingStatus.DONE
            kb.save(update_fields=["teks", "processing_status", "processing_error"])

    except ExtractionError as exc:
        kb.processing_status = ProcessingStatus.FAILED
        kb.processing_error = str(exc)
        kb.save(update_fields=["processing_status", "processing_error"])
    except Exception as exc:  # jangan sembunyikan error (bagian 37) -- catat, jangan mock
        kb.processing_status = ProcessingStatus.FAILED
        kb.processing_error = f"Error tak terduga: {exc}"
        kb.save(update_fields=["processing_status", "processing_error"])

    return kb
