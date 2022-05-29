from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject

dst_layout = []
start_from = 1

# FN = "Sufi Wisdom ORACLE.pdf"
FN = "nums.pdf"

transposition = [
    [1, 14, 3, 12, 5, 10, 7, 8], # front
    [15, 0, 13, 2, 11, 4, 9, 6], # back
]

pages_on_multipage = 4
pages_in_group = 2
group_size = pages_on_multipage*pages_in_group

pages = [[],[]]

with open(FN, 'rb') as r:
    reader = PdfFileReader(r)

    N = reader.getNumPages()

    if N-1 < start_from:
        raise "Not enough pages"

    page = reader.getPage(start_from)
    W = page.mediaBox.getWidth()
    H = page.mediaBox.getHeight()
    dst_layout = [
        [1, 0, H],
        [1, W, H],
        [1, 0, 0],
        [1, W, 0],
    ]

    # two writers for front and back
    writers = [PdfFileWriter(), PdfFileWriter()]

    group_start_offset = start_from
    out_page = None
    pfb = None
    while group_start_offset < N:
        print(f"group offset {group_start_offset}")
        for fb in range(0,2):
            for i in range(0, group_size):
                print(f"fb={fb}, i={i}")
                if i % pages_on_multipage == 0:
                    # append page to list
                    if out_page != None:
                        print(f"page to {pfb}")
                        writers[pfb].addPage(out_page)
                    # start a new page
                    out_page = PageObject.createBlankPage(None, W*2, H*2)
                    # where next page will go
                    pfb = fb

                print(f"place page {group_start_offset + transposition[fb][i]} in {i%4} slot")
                page = reader.getPage(group_start_offset + transposition[fb][i])
                out_page.mergeScaledTranslatedPage(page, *dst_layout[i % 4])

        group_start_offset += 2*group_size

    # append last page to list
    if out_page != None:
        print(f"page to {pfb}")
        writers[pfb].addPage(out_page)

    with open('front.pdf', 'wb') as f:
    	writers[0].write(f)
    with open('back.pdf', 'wb') as f:
    	writers[1].write(f)

# reader = PdfFileReader(open("invoice.pdf",'rb'))
# invoice_page = reader.getPage(0)
# sup_reader = PdfFileReader(open("supplement.pdf",'rb'))
# sup_page = sup_reader.getPage(1)  # We pick the second page here
#
# out_page = PageObject.createBlankPage(None, sup_page.mediaBox.getWidth(), sup_page.mediaBox.getHeight())
# out_page.mergeScaledTranslatedPage(sup_page, 1, 0, -400)  # -400 is approximate mid-page
#
# translated_page.mergePage(invoice_page)
#
# writer = PdfFileWriter()
# writer.addPage(translated_page)
#
# with open('out.pdf', 'wb') as f:
# 	writer.write(f)
