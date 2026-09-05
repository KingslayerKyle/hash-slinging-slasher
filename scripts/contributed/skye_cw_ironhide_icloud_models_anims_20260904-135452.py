"""Strict filenames from Skye's public, individual CW .410 Ironhide iCloud export.

The public UGX hub links this archive separately.  Its Apple iCloud short GUID
is resolved through the public CloudKit record endpoint.  Only exact filenames
with native export extensions are emitted; no output path, GDT/script text,
image export composite, or incomplete audio path is made into a candidate.
"""

import base64
import io
import json
import urllib.request
import zipfile

GUID = "0f7LEFZ24ypwmvgIVvJXjOJtw"
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
    with urllib.request.urlopen(archive_url(), timeout=300) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    names = {
        path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for path in archive.namelist()
        if path.endswith((".xmodel_bin", ".xanim_bin"))
    }
    print("\n".join(sorted(names)))
