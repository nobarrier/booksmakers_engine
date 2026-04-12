from erp.models import Document, DocumentItem
from erp.erputils import generate_doc_no


def generate_po(document):
    po = Document.objects.create(
        doc_type="PO",
        doc_no=generate_doc_no("PO"),
        company=document.company,
        date=document.date,
        usage="발주서 자동 생성",
    )

    for item in document.items.all():
        DocumentItem.objects.create(
            document=po,
            row_no=item.row_no,
            name=item.name,
            spec=item.spec,
            unit=item.unit,
            qty=item.qty,
            price=item.price,
            amount=item.amount,
            remark=item.remark,
        )

    return po
