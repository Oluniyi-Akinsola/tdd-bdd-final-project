######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "/"  # delete once READ is implemented
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

@app.route("/products", methods=["GET"])
def get_all_products():
    """ gets all products """
    products = []
    name_arg = request.args.get("name")
    cat_arg = request.args.get("category")
    avail_arg = request.args.get("available")

    if name_arg:
        app.logger.info("find by name: %s", name_arg)
        products = Product.find_by_name(name_arg)
    elif cat_arg:
        app.logger.info("find by category: %s", cat_arg)
        enum_val = getattr(Category, cat_arg.upper())
        products = Product.find_by_category(enum_val)
    elif avail_arg:
        app.logger.info("find by available: %s", avail_arg)
        products = Product.find_by_availability(bool(avail_arg))
    else:
        app.logger.info("returning all products")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return results, status.HTTP_200_OK

######################################################################
# R E A D   A   P R O D U C T
######################################################################

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """ gets product by id """
    found = Product.find(product_id)
    if not found:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id [{product_id}] not found")

    app.logger.info("returning product %s found by id %s", found.name, found.id)
    return found.serialize(), status.HTTP_200_OK

######################################################################
# U P D A T E   A   P R O D U C T
######################################################################

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """ updates existing product by product_id """
    check_content_type("application/json")

    found = Product.find(product_id)
    if not found:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id [{product_id}] not found")

    app.logger.info("attempting update on product %s with id %s", found.name, found.id)

    found.deserialize(request.get_json())
    found.id = product_id
    found.update()

    return found.serialize(), status.HTTP_200_OK

######################################################################
# D E L E T E   A   P R O D U C T
######################################################################


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """ delete product by product_id """
    found = Product.find(product_id)
    if not found:
        abort(status.HTTP_404_NOT_FOUND, f"Product with product_id [{product_id}] not found")

    app.logger.info("attempting delete on product %s with product_id %s", found.name, found.id)

    found.delete()

    return "", status.HTTP_204_NO_CONTENT