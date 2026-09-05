"""Strict model/animation filenames from Skye's public CW Weapon Common export.

This is the shared support bundle linked separately by Skye's UGX BO:CW hub.
It is resolved through Apple's public CloudKit endpoint and read directly from
the public ZIP.  Only literal .xmodel_bin and .xanim_bin basenames are emitted:
paths, source/GDT files, exporter image composites, and incomplete sound paths
are deliberately not converted into putative game names.
"""

import base64
import io
import json
import urllib.request
import zipfile

GUID = "0d7YBUnLD5XTlnXFFn9e6qNyQ"
RESOLVE = "https://ckdatabasews.icloud.com/database/1/com.apple.clouddocs/production/public/records/resolve"


def archive_url() -> str:
    request = urllib.request.Request(
        RESOLVE,
        data=json.dumps({"shortGUIDs": [{"value": GUID}]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        fields = json.load(response)["results"][0]["rootRecord"]["fields"]
    filename = base64.b64decode(fields["encryptedBasename"]["value"]).decode()
    return fields["fileContent"]["value"]["downloadURL"].replace(
        "${f}", filename + "." + fields["extension"]["value"]
    )


if __name__ == "__main__":
    with urllib.request.urlopen(archive_url(), timeout=600) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    names = {
        path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for path in archive.namelist()
        if path.endswith((".xmodel_bin", ".xanim_bin"))
    }
    print("\n".join(sorted(names)))
