"""Strict model/animation filenames from Skye's public CW M79 iCloud export.

The public UGX hub links this as an individual archive.  It does contain WAVs,
but every one is below the port-only `sound_assets/skye_ports/` staging path;
without a retained original full game path or explicit alias field they are not
sound candidates.  Emit only literal .xmodel_bin and .xanim_bin basenames.
"""

import base64
import io
import json
import urllib.request
import zipfile

GUID = "091KGhWk0x1d3KPrOMFre7oiQ"
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
