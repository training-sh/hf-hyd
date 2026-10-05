"""Generate a tiny text PDF using only the standard library."""
from pathlib import Path

lines = ["DemoMart - SYNTHETIC TRAINING INVOICE", "Invoice: INV1001", "Order: O1001",
         "Customer: C101 (Asha)", "Currency: INR", "",
         "Product     Quantity     Unit price     Line total",
         "P101        2            1299.00        2598.00",
         "P102        1             899.00         899.00", "",
         "Subtotal: 3497.00", "GST (18%): 629.46", "Total: 4126.46",
         "Payment status: not supplied"]
stream = "BT /F1 12 Tf 50 790 Td 18 TL\n"
for i, line in enumerate(lines):
    escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream += ("T* " if i else "") + f"({escaped}) Tj\n"
stream += "ET"
objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
           b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
           b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
           f"<< /Length {len(stream.encode())} >>\nstream\n{stream}\nendstream".encode()]
output = b"%PDF-1.4\n"
offsets = [0]
for i, obj in enumerate(objects, 1):
    offsets.append(len(output))
    output += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
xref = len(output)
output += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
output += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
output += f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
target = Path(__file__).resolve().parent / "data" / "invoice-INV1001.pdf"
target.write_bytes(output)
print(target)
