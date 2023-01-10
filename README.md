# doc-search

Preview should be available at http://167.99.253.189:8000/docs

### Search patterns

1. *Stop words:* `!KAMAZ` - exclude documents that contain `!KAMAZ`
2. *Prefix match:* `55*` - search documents that contain words starting from `55`.

### Supported formats

1. Scanned PDF
2. Text PDF

## Endpoints

View the interactive docs http://localhost:40111/docs

### Add document

    curl -X 'POST' \
      'http://localhost:40111/documents/?meta=%7B%22color%22%3A%20%22true%22%7D' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@sample.color.pdf;type=application/pdf'

Response body:

    {
      "id": "8070eba4-cc5b-4ba0-8a5e-9f290ef7c7ea",
      "status": "PENDING",
      "meta": {
        "color": "true"
      }
    }

### Search documents

    curl -X 'GET' \
      'http://localhost:40111/search?query=%D0%BF%D0%B0%D0%BF%D0%B5%D1%80%D0%BE%D0%B2%D0%B8%D1%85%20%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%96%D0%B2' \
      -H 'accept: application/json'

Response body:

    [
      {
        "id": "1c71246b-1ac4-43fb-b5d7-634aa65e6ad4",
        "status": "OK",
        "meta": {
          "color": "true"
        }
        "headline": "..."
      },
      {
        "id": "8070eba4-cc5b-4ba0-8a5e-9f290ef7c7ea",
        "status": "OK",
        "meta": {
          "color": "true"
        }
        "headline": "..."
      }
    ]

### Highlight pages in document

    curl -X 'GET' \
      'http://localhost:40111/documents/ea2d3679-de61-4892-b3aa-f62c3a6f68c6/highlights?query=opel%20WOLF%2A' \
      -H 'accept: application/json'

Response body:

    [
      {
        "page_number": 2,
        "headline": "<b>Opel</b> ; Модель: Vivaro;...."
      }
    ]

## Local run

### Install requirments

    sudo apt-get install postgresql tesseract-ocr tesseract-ocr-all python3-pip uvicorn
    pip3 install -r requirments.txt

### Prepare the DB

    psql -d documents -h localhost -U postgres < sql/schema.sql

#### Install ukrainian support

Download two parts of dictionary and add them to postgress:

    wget https://github.com/brown-uk/dict_uk/releases/download/v5.9.0/hunspell-uk_UA_5.9.0.zip
    unzip hunspell-uk_UA_5.9.0.zip
    sudo cp uk_UA.aff `pg_config --sharedir`/tsearch_data/uk_UA.affix
    sudo cp uk_UA.dic `pg_config --sharedir`/tsearch_data/uk_UA.dict

    wget https://raw.githubusercontent.com/brown-uk/dict_uk/v5.9.0/distr/postgresql/ukrainian.stop
    sudo cp ukrainian.stop `pg_config --sharedir`/tsearch_data/ukrainian.stop

    psql -h localhost -U postgres < sql/uk_ua_search.sql

### Start

    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/ uvicorn main:app --reload --host 0.0.0.0 --port 40111

    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/ uvicorn main:app --workers 4 --host 0.0.0.0 --port 40111
