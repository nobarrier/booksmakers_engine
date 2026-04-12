from erp.models import Document, DocumentItem, BOMLine
from datetime import datetime


# =========================
# 문서번호 생성 (표준)
# =========================
def generate_doc_no(doc_type):
    today_str = datetime.now().strftime("%Y%m%d")
    today_date = datetime.now().date()

    count = Document.objects.filter(doc_type=doc_type, date=today_date).count() + 1

    return f"{doc_type}-{today_str}-{count:03d}"


# =========================
# BOM → PR 생성
# =========================
def create_pr_from_bom(group, company):
    doc = Document.objects.create(
        doc_type="PR",
        doc_no=generate_doc_no("PR"),
        company=company,
        date=datetime.now().date(),
        usage="BOM 자동 생성",
    )

    total = 0

    lines = BOMLine.objects.filter(group=group).order_by("row_no")

    for line in lines:
        amount = (line.qty or 0) * (line.unit_price or 0)

        DocumentItem.objects.create(
            document=doc,
            row_no=line.row_no,
            name=line.item_name,
            spec=line.spec,
            unit=line.unit,
            qty=line.qty or 0,
            price=line.unit_price or 0,
            amount=amount,
            remark=line.remark,
        )

        total += amount

    doc.total_amount = total
    doc.save()

    return doc
