#!/usr/bin/python
# -- coding: utf-8 --

'''
requires reportlab and pyPDF for normal use
for windows printing requires win32api
or ghostscript and ghostview

Usage: txt2pdf.py [options] text_file
The name of the outfile is the name on the text_file with pdf extension.

Options:
  -h, --help            show this help message and exit
  -c COPIES, --copies=COPIES
                        number of copies, only valid with -p option
  -g                    print through ghostprint, only valid with -w option
  -m                    use half letter as size of output, default letter
  --output=OUTPUT       use specific output file name
  -p, --print           print file after converting
  --printer=PRINTER     printer to send file, default: send to default printer
  -w                    use win32api to send file to print, only valid with -p
                        option
                        
'''

import sys
import os
import optparse
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from pyPdf import PdfFileWriter, PdfFileReader

DOC_WIDTH, DOC_HEIGHT = letter
COPIAS=1

def Y(y):
    '''
    Changes 'y' origin from page bottom to page top
    '''
    return DOC_HEIGHT - y


media_carta = Y((DOC_HEIGHT / 2) - 1*cm)
carta =  Y((DOC_HEIGHT) - 7.7*cm)

usage = "usage: %prog [options] text_file\n" + \
        "The name of the outfile is the name on the text_file with pdf extension." 
parser = optparse.OptionParser(usage=usage)

parser.set_defaults(copies=COPIAS)
parser.set_defaults(letter_size=True)
parser.set_defaults(linux=True)
parser.set_defaults(printing=False)
parser.set_defaults(ghost=False)
parser.set_defaults(printer=None)

parser.add_option('-c', '--copies', help='number of copies, only valid with -p option',
                  dest='copies', type='int')
parser.add_option('-g', help='print through ghostprint, only valid with -w option',
                  dest='ghost', action='store_true')
parser.add_option('-m',  help='use half letter as size of output, default letter',
                  dest='letter_size', action='store_false')
parser.add_option('--output',  help='use specific output file name',
                  dest='output', action='store')
parser.add_option('-p', '--print', help='print file after converting',
                  dest='printing', action='store_true')
parser.add_option('--printer', help='printer to send file, default: send to default printer',
                  dest='printer', action='store')
parser.add_option('-w', help='use win32api to send file to print, only valid with -p option',
                  dest='linux', action='store_false')

(opts, args) = parser.parse_args()


def filter_non_printable(str):
    '''
    Remove non printable characters
    '''
    return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])


def txt2pdf(archivo, pdf, letter_size=True):
    '''
    Function that actualy converts text to pdf
    '''
    c = Canvas(pdf, pagesize=letter)
    c.setFont('Courier-Bold', 7)
    x = 0.5*cm     # controls de left margin
    t = Y(0.5*cm)  # controls de top margin
    inc = 0.3*cm   # controls the line spacing
    y = t          # set y coord to top margin
    if letter_size:
       brk = carta
    else:
       brk = media_carta
    f = open(archivo)

    for line in f.readlines():
        l = filter_non_printable(line)
        y -= inc
        c.drawString(x,y,l)
        if y < brk:
            c.showPage()
            c.setPageSize(letter)
            c.setFont('Courier-Bold', 7)
            y = t

    f.close()
    c.save()


def pdfRemoveBlank(archivo):
    '''
    Remove any blank pages at the end of the pdf file
    '''
    f = file(archivo,"rb")
    input = PdfFileReader(f)
    output = PdfFileWriter()

    for i in range(input.getNumPages()):
        p = input.getPage(i)
        x = p.extractText()
        if len(x.strip()) > 0:
            output.addPage(p)

    outputStream = file("tmp.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
    del input
    f.close()
    os.remove(archivo)
    os.rename('tmp.pdf', archivo)


def print_pdf(archivo, copias = 1, printer=None):
    '''
    Print using windows printer (API) needs win32api
    Print de default printer.
    ToDo: print to non-default printer
    '''
    import win32api
    for i in range(copias):
        win32api.ShellExecute(0,"print", f, None,".",0)
        
        
def ghost_print(archivo, copias = 1, printer=None):
    '''
    Print via ghostview and ghostscript to windows printer.
    Needs ghostscript and ghostview to be installed in win computer
    '''
    import subprocess
    for i in range(copias):
        if printer:
            p = subprocess.Popen(["gsprint.exe", archivo, "-printer %s" % printer],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            p = subprocess.Popen(["gsprint.exe", archivo],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()


def linux_print(archivo, copias = 1, printer=None):
    '''
    Print via lp printer.
    '''
    import subprocess
    if printer:
        p = subprocess.Popen(["lp -n %d" % copias, "-d %s" % printer, archivo],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen(["lp -n %d" % copias, archivo],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()


if __name__ == "__main__":

    if len(args) <> 1:
        parser.print_help()
        exit(1)

    try:
        nombre, extension = args[0].split('.')
    except:
        nombre = args[0]

    if opts.output:
        f = opts.output
    else:
        f = "%s.pdf" % nombre

    txt2pdf(args[0],f,opts.letter_size)
    pdfRemoveBlank(f)
    
    if opts.printing:
        if opts.linux:
            linux_print(f,opts.copies,opts.printer)
        else:
            if opts.ghost:
                ghost_print(f,opts.copies,opts.printer)
            else:
                print_pdf(f,opts.copies,opts.printer)
