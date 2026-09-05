"""Strict model/animation filenames from Skye's public CW Type 63 iCloud export.

The individual package is linked by Skye's UGX BO:CW weapon hub.  Resolve the
public CloudKit short GUID, enumerate its ZIP, and emit only exact native
.xmodel_bin and .xanim_bin basenames.  It deliberately rejects all port
placement paths, source/GDT labels, image composites, and incomplete sounds.
"""

import base64
import io
import json
import urllib.request
import zipfile

GUID = "0d5kzCUO63cYSffmG87a3fAsg"
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
