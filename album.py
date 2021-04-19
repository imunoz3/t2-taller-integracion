from flask import Flask
from flask_restful import reqparse, abort, Resource
from base64 import b64encode

album_parser = reqparse.RequestParser()
album_parser.add_argument('name', type=str, help='Name of album')
album_parser.add_argument('genre', type=int, help='Genre of album')
