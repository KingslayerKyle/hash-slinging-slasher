"""Literal model and animation filenames from Skye's public CW 1911 iCloud export.

The source ZIP is `Skye_CW_1911.zip`, shared from the original UGX release page.
Only basenames physically present as .xmodel_bin/.xanim_bin are included.  Port
placement paths, GDT text, combined exporter image names, and audio paths are
intentionally not treated as game labels.
"""

MODELS = """\
am_t9_1911
am_t9_1911_fdw
vm_t9_1911
vm_t9_1911_extmag2
vm_t9_1911_ldw
vm_t9_1911_ldw_up
vm_t9_1911_long_slide2
vm_t9_1911_long_slide2+mix_muzzle
vm_t9_1911_mag
vm_t9_1911_mix_handle
vm_t9_1911_mix_muzzle
vm_t9_1911_slide
wm_t9_1911
wm_t9_1911_extmag2
wm_t9_1911_grenade
wm_t9_1911_ldw
wm_t9_1911_ldw_up
wm_t9_1911_long_slide2
wm_t9_1911_long_slide2+mix_muzzle
wm_t9_1911_mag
wm_t9_1911_mix_handle
wm_t9_1911_mix_muzzle
wm_t9_1911_slide
""".splitlines()

ANIMS = """\
am_t9_1911_ads_down
am_t9_1911_ads_fire
am_t9_1911_ads_up
am_t9_1911_crawl_back
am_t9_1911_crawl_forward
am_t9_1911_crawl_in
am_t9_1911_crawl_left
am_t9_1911_crawl_out
am_t9_1911_crawl_right
am_t9_1911_fdw_crawl_back
am_t9_1911_fdw_crawl_forward
am_t9_1911_fdw_crawl_in
am_t9_1911_fdw_crawl_left
am_t9_1911_fdw_crawl_out
am_t9_1911_fdw_crawl_right
am_t9_1911_fdw_first_raise
am_t9_1911_fdw_inspect
am_t9_1911_fdw_pullout
am_t9_1911_fdw_putaway
am_t9_1911_fdw_slide_idle
am_t9_1911_fdw_sprint_in
am_t9_1911_fdw_sprint_loop
am_t9_1911_fdw_sprint_out
am_t9_1911_fire
am_t9_1911_first_raise
am_t9_1911_idle
am_t9_1911_inspect
am_t9_1911_ldw_fire
am_t9_1911_ldw_idle
am_t9_1911_ldw_reload
am_t9_1911_ldw_reload_empty
am_t9_1911_pullout
am_t9_1911_putaway
am_t9_1911_rdw_fire
am_t9_1911_rdw_idle
am_t9_1911_rdw_reload
am_t9_1911_rdw_reload_empty
am_t9_1911_reload
am_t9_1911_reload_empty
am_t9_1911_slide_air_in
am_t9_1911_slide_in
am_t9_1911_slide_loop
am_t9_1911_slide_out
am_t9_1911_sprint_in
am_t9_1911_sprint_loop
am_t9_1911_sprint_out
""".splitlines()

if __name__ == "__main__":
    print("\n".join(MODELS + ANIMS))
