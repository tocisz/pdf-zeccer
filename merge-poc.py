import pprint
from os import close
from decimal import Decimal

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject

dst_layout = []
start_from = 6
# start_from = 1
finish_at = 210
# finish_at = 16

start_from -= 1 # make first page no 0

FN = "The Wild Unknown Animal Spirit tarot Deck.pdf"
# FN = "nums.pdf"

transposition = [
    [11, 4, 12, 3, 9, 6, 14, 1], # front
    [5, 10, 2, 13, 7, 8, 0, 15], # back
]

pages_on_multipage = 4
pages_in_group = 2
group_size = pages_on_multipage*pages_in_group

MM_TO_PT = Decimal('2.83465')

A4_W = Decimal(595)
A4_H = Decimal(842)

GUTTER = Decimal(72) # 1 inch

pages = [[],[]]

cross = None

cross_file = open('cross.pdf', 'rb')
cross_reader = PdfFileReader(cross_file)
cross = cross_reader.getPage(0)

def putCross(page, x, y):
    page.mergeTranslatedPage(cross, x-MM_TO_PT, y-MM_TO_PT)

def calculateScale(w, h):
    return min(
        (A4_W-GUTTER) / (2*w),
        A4_H / (2*h)
    )

with open(FN, 'rb') as r:
    reader = PdfFileReader(r)

    N = min(reader.getNumPages(), finish_at)

    if N-1 < start_from:
        raise "Not enough pages"

    page = reader.getPage(start_from)
    W = page.mediaBox.getWidth()
    H = page.mediaBox.getHeight()

    scale = calculateScale(W, H)

    def calculateLayout():
        w = W*scale
        h = H*scale
        cx = A4_W/2
        cy = A4_H/2
        return [
            [0, scale, cx-GUTTER/2-w, cy],
            [0, scale, cx+GUTTER/2, cy],
            [180, scale, w+ cx-GUTTER/2-w, h+cy-h], #w+ bacause of rotation
            [180, scale, w+ cx+GUTTER/2, h+cy-h],
        ]
    dst_layout = calculateLayout()

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
                        putCross(out_page, A4_W/2, A4_H/2 - H*scale)
                        putCross(out_page, A4_W/2, A4_H/2)
                        putCross(out_page, A4_W/2, A4_H/2 + H*scale)
                        print(f"page to {pfb}")
                        pages[pfb].append(out_page)
                    # start a new page
                    out_page = PageObject.createBlankPage(None, A4_W, A4_H)
                    # where next page will go
                    pfb = fb

                sn = group_start_offset + transposition[fb][i]
                if sn < N:
                    print(f"place page {sn} in {i%4} slot")
                    page = reader.getPage(sn)
                    out_page.mergeRotatedScaledTranslatedPage(page, *dst_layout[i % 4])
                else:
                    print(f"skip page {sn} (> {N})")

        group_start_offset += 2*group_size

    # append last page to list
    if out_page != None:
        print(f"page to {pfb}")
        pages[pfb].append(out_page)

    writer = PdfFileWriter()
    for p in pages[0]:
        writer.addPage(p)
    with open('front.pdf', 'wb') as f:
    	writer.write(f)

    writer = PdfFileWriter()
    for p in reversed(pages[1]):
        writer.addPage(p)
    with open('back.pdf', 'wb') as f:
    	writer.write(f)

if cross_file:
    cross_file.close()