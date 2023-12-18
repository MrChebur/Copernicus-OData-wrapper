# Copernicus OData wrapper

This is a Python wrapper of
the [Copernicus Open Data Protocol API](https://documentation.dataspace.copernicus.eu/APIs/OData.html).

It is designed to make it easier to send requests.

> [!IMPORTANT]
> This wrapper is not intended to download data. It has no such functions.

For example, using this wrapper you can:

- Filter products by various attributes (coordinates, cloud coverage, date ranges, collection name, etc)
- Get a download url for a specific product (i.e. Sentinel-2 Level 1C product with the name
  of `S2A_MSIL1C_20230702T064631_N0509_R020_T42VWN_20230702T073123.SAFE`)

Usage example: [example_usage.py](/examples/example_usage.py)

<!-- This content will not appear in the rendered Markdown

**This is bold text**
_This text is italicized_
> Text that is a quote

![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://myoctocat.com/assets/images/base-octocat.svg)
 -->
