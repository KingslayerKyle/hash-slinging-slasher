"""Strict filenames from Skye's public, individual CW C58 iCloud export.

Unlike the unavailable bulk Weapon Common bundle, the UGX hub links this archive
directly.  The iCloud short GUID is resolved through Apple's public CloudKit
record endpoint; only literal .xmodel_bin and .xanim_bin basenames in its ZIP
are emitted.  It intentionally excludes paths, GDT/script text, image export
composites, and audio filenames lacking their original full game path.
"""

import io
import json
import urllib.request
import zipfile

GUID = "0d4NgRk_us0fyWCg5Gn6f9Piw"
RESOLVE = "https://ckdatabasews.icloud.com/database/1/com.apple.clouddocs/production/public/records/resolve"


def archive_url() -> str:
    request = urllib.request.Request(
        RESOLVE,
        data=json.dumps({"shortGUIDs": [{"value": GUID}]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        record = json.load(response)["results"][0]["rootRecord"]["fields"]
    name = json.loads(json.dumps(record["encryptedBasename"]["value"]))
    # Apple encodes the basename as ordinary base64, not a candidate name.
    import base64
    filename = base64.b64decode(name).decode() + "." + record["extension"]["value"]
    return record["fileContent"]["value"]["downloadURL"].replace("${f}", filename)


if __name__ == "__main__":
    with urllib.request.urlopen(archive_url(), timeout=300) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    names = {
        path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for path in archive.namelist()
        if path.endswith((".xmodel_bin", ".xanim_bin"))
    }
    print("\n".join(sorted(names)))
