from erp.models import Document, DocumentItem
from erp.erputils import generate_doc_no


def generate_rfq_from_pr(document):
    rfq = Document.objects.create(
        doc_type="RFQ",
        doc_no=generate_doc_no("RFQ"),
        company=document.company,
        date=document.date,
        usage="견적요청 자동 생성",
    )

    for item in document.items.all():
        DocumentItem.objects.create(
            document=rfq,
            row_no=item.row_no,
            name=item.name,
            spec=item.spec,
            unit=item.unit,
            qty=item.qty,
            price=0,
            amount=0,
            remark=item.remark,
        )

    return rfq
