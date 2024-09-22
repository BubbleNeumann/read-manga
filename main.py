import requests as r
import re
import os


def get_pic_urls(url: str) -> list[str]:

    from bs4 import BeautifulSoup as bs

    response = r.get(url)
    soup = bs(response.text, 'html.parser')
    img_tags=soup.find_all('img')
    return [img['src'].strip() for img in img_tags if img['src'].endswith('.jpeg') and 'discord' not in img['src']]


def download_pics(pic_urls: list[str], folder_name = 'tmp') -> None:
    filename_regex = re.compile(r'/([\w_-]+[.]jpeg)$')

    for url in pic_urls:
        filename = filename_regex.search(url).group(1)

        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

        with open(f'{folder_name}/{filename}', 'wb') as f:
            response = r.get(url)
            f.write(response.content)


def combine_pics_into_pdf(pdf_name:str, folder_name = 'tmp') -> None:

    def key_func(filename: str):
        digits = filename.split('.')[0]
        try:
            return int(digits)
        except:
            return 10000


    from PIL import Image
    from fpdf import FPDF
    pdf = FPDF()
    w,h = 1,1

    first = True
    for file in sorted(os.listdir(folder_name), key=key_func):
        if first:
            cover = Image.open(f'{folder_name}/{file}')
            w,h = cover.size
            pdf = FPDF(unit = "pt", format = [w,h])
        first = False
        image = f'{folder_name}/{file}'
        pdf.add_page()
        pdf.image(image,0,0,w,h)
        print(f'{file} done')
    pdf.output(pdf_name, "F")


def cleanup(folder_name = 'tmp'):
    for file in os.listdir(folder_name):
        os.remove(f'{folder_name}/{file}')
    os.rmdir(folder_name)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-l", "--link", dest="link", help="link to the manga chapter")
    args = parser.parse_args()

    url = args.link

    download_pics(get_pic_urls(url))
    name_components = [e for e in url.split('/') if e != '']
    name = '-'.join(name_components[-2:]) + '.pdf'

    combine_pics_into_pdf(name)
    cleanup()

if __name__ == '__main__':
    main()
