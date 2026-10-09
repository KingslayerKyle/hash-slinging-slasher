"""BO7 weapon codenames guessed from the themes the known ones follow, for the weapon-slot plan.

Every known BO7 weapon is `sat_<class>_<word>` and each class draws its words from one theme
(measured 2026-10-09 on the 77 known): ar = birds (hawk finch condor egret eagle vulture kite
macaw falcon kiwi heron wren albatross), sm = animals (orca komodo puma zebra cobra gecko bear
hyena otter bengal marmot serval stoat), sh = dog breeds (corso akita husky shepherd terrier),
sn/dm = seas and gulfs (caspian baltic aden coral solomon samar kara oman scotia tasman), pi/me =
stars (alcor orion atlas timir saiph nashira castor elnath), lm = myth (hades typhon zeus avalon
hildr). A weapon that has no named asset yet is missing from every list, so nothing built from
known names can reach any of its assets; these words are the guess at what it is called.

Writes contrib/themed_weapon_codes.txt (`<class>_<word>` and `<class>_<word>exotic`, every word
under its theme's classes) and contrib/themed_weapon.plan.txt, which crosses them with the top
beginnings/endings that contrib/weapon_slot_plan.py measured around known weapons.

    python contrib/weapon_slot_plan.py && python contrib/themed_weapons.py
    confirm_plan contrib/themed_weapon.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"

BIRDS = """albatross auk avocet barbet bittern blackbird bluebird bobolink booby bulbul bunting bustard
buzzard canary capercaillie caracara cardinal cassowary catbird chaffinch chickadee chough condor
coot cormorant corncrake cowbird crane crossbill crow cuckoo curlew dipper dodo dotterel dove
drongo duck dunlin dunnock eagle egret eider emu falcon finch flamingo flicker flycatcher frigate
fulmar gadwall gannet garganey godwit goldcrest goldfinch goose goshawk grackle grebe greenfinch
grosbeak grouse guillemot gull gyrfalcon harrier hawk heron hobby honeyeater hoopoe hornbill
hummingbird ibis jacana jackdaw jaeger jay junco kestrel killdeer kingbird kingfisher kinglet kite
kittiwake kiwi knot kookaburra lapwing lark linnet loon lorikeet lory lovebird lyrebird macaw
magpie mallard martin meadowlark merganser merlin mockingbird moorhen motmot murre mynah nighthawk
nightingale nightjar nuthatch oriole osprey ostrich ouzel owl oystercatcher parakeet parrot
partridge peacock pelican penguin peregrine petrel phalarope pheasant phoebe pigeon pintail pipit
plover potoo ptarmigan puffin quail quetzal rail raven razorbill redstart rhea roadrunner robin
rook ruff sanderling sandpiper sapsucker scaup scoter secretary shearwater shoebill shrike siskin
skimmer skua skylark snipe sparrow sparrowhawk spoonbill starling stilt stork storm sunbird swallow
swan swift tanager teal tern thrasher thrush tit toucan towhee treecreeper trogon turaco turkey
turnstone vireo vulture wagtail warbler waxwing weaver wheatear whimbrel whippoorwill wigeon
woodcock woodpecker wren wryneck yellowhammer harpy hornet jabiru kea kakapo takahe tui weka
moa roc griffin phoenix raptor hawkeye sparrowhawk shrike seahawk nightowl""".split()
ANIMALS = """aardvark addax agouti alpaca anaconda anteater antelope armadillo asp axolotl baboon
badger bandicoot barracuda basilisk bat bear beaver bison boa boar bobcat bongo bonobo buffalo
bull bushbaby caiman camel capybara caracal caribou cassowary cat chameleon cheetah chimp
chinchilla chipmunk civet coati cobra cougar coyote crocodile dingo dhole dolphin donkey dormouse
dugong eland elephant elk ermine ferret fennec fox gaur gazelle gecko gerbil gharial gibbon gila
giraffe gnu goat gopher gorilla grizzly groundhog guanaco hamster hare hedgehog hippo honeybadger
hyena hyrax ibex iguana impala jackal jaguar jaguarundi jerboa kangaroo kinkajou koala komodo
kudu lemur leopard liger lion llama lynx macaque mamba manatee mandrill mangabey mantis margay
marmoset marmot marten meerkat mink mole mongoose monitor moose mouse mule muskox muskrat narwhal
numbat ocelot okapi opossum orangutan orca oryx otter panda pangolin panther peccary pika platypus
polecat porcupine porpoise possum puma python quokka quoll rabbit raccoon rat rattler reindeer
rhino sable saiga salamander seal serval shark sheep shrew skink skunk sloth snake springbok
squirrel stoat tapir tarsier tasmanian taipan tiger tortoise vicuna viper vole wallaby walrus
warthog weasel whale wildcat wildebeest wolf wolverine wombat yak zebra zebu badger bengal
ocelot jackrabbit ratel bobcat cobra adder krait mamba coyote hound stingray piranha moray
scorpion tarantula hornet wasp raptor gator mako hammerhead""".split()
DOGS = """affenpinscher afghan airedale akita alsatian basenji basset beagle bichon bloodhound
borzoi boxer briard brittany bulldog bullmastiff cairn chihuahua chow collie corgi corso dalmatian
dachshund dane deerhound dingo doberman elkhound foxhound greyhound griffon harrier havanese
husky keeshond kelpie komondor kuvasz labrador laika leonberger lurcher malamute malinois
maltese mastiff mudi newfoundland otterhound papillon pekingese pinscher pointer pomeranian poodle
pug puli pyrenees retriever rottweiler saluki samoyed schnauzer setter sharpei sheepdog shepherd
shiba shihtzu sloughi spaniel spitz terrier vizsla weimaraner whippet wolfhound xolo boerboel
cane kangal ovcharka tosa presa dogo fila ridgeback hokkaido kishu jindo azawakh catahoula
coonhound bluetick redbone plott beauceron bouvier hovawart""".split()
SEAS = """adriatic aegean alboran amundsen andaman arabian arafura aral arctic atlantic azov baffin
balearic bali banda barents beaufort bering bismarck black bohol caribbean caspian celebes celtic
ceram chukchi coral crete dead east flores halmahera hebrides indian ionian irish japan java kara
labrador laccadive laptev ligurian marmara mediterranean molucca natuna north norwegian okhotsk
pacific philippine red ross salish sargasso savu scotia sibuyan solomon south sulu tasman timor
tyrrhenian wadden weddell white yellow aden oman persian bothnia finland riga mexico california
alaska bengal biscay cadiz carpentaria guinea panama paria siam suez thailand tonkin fundy hudson
baltic adriatic marmara samar visayan camotes mindanao davao moro sulu camiguin bohai chesapeake
cook drake magellan bass hormuz malacca sunda lombok makassar gibraltar bosporus dardanelles
messina otranto kerch skagerrak kattegat oresund dover florida yucatan""".split()
STARS = """acamar achernar acrux adhara albireo alcor alcyone aldebaran alderamin algenib algieba
algol alhena alioth alkaid almach alnair alnilam alnitak alphard alphecca alpheratz altair
aludra ankaa antares arcturus arneb ascella aspidiske atlas atria avior bellatrix betelgeuse
canopus capella caph castor cebalrai deneb denebola diphda dubhe elnath eltanin enif fomalhaut
gacrux gienah hadar hamal izar kaus kochab larawag markab megrez menkalinan menkar menkent merak
miaplacidus mintaka mira mirach mirfak mirzam mizar naos nashira nunki orion peacock phact phecda
polaris pollux procyon rasalhague regulus rigel rigil ruchbah sabik sadr saiph sargas scheat
schedar shaula sheliak sirius spica suhail tarazed thuban timir unukalhai vega wezen zaurak
zubenelgenubi zosma maia merope electra taygeta celaeno sterope pleione vindemiatrix sadalsuud
sadalmelik albali skat ancha alrescha mesarthim sheratan botein menkib atik zaniah porrima
heze syrma khambalia elgafar chara cor caroli tania alula talitha muscida alkes alsciaukat
nekkar seginus kornephoros rasalgethi sarin maasym marfik yed cujam cursa keid azha acamar
beid tureis aspidiske naos suhail markeb tegmine tarf acubens asellus altarf""".split()
MYTH = """achilles aegis aeolus ajax amun anubis aphrodite apollo ares argus artemis asgard athena
atlas aurora avalon baldur bastet boreas cerberus chaos charon chimera chronos circe cronus
cyclops daedalus demeter dionysus eos erebus eris eros freya freyr frigg gaia hades heimdall
helios hephaestus hera hercules hermes hestia hildr hydra hyperion icarus janus jupiter kraken
loki mars medusa mercury minerva minotaur mjolnir neptune nemesis nike njord nyx oberon odin
olympus orion osiris pandora pegasus persephone perseus phoebe pluto poseidon prometheus ra
ragnarok rhea selene set sif skadi sol surtr thanatos thor titan triton tyr typhon ulysses
uranus valhalla valkyrie vulcan ymir zephyr zeus fenrir garm hel brynhild sigurd tyrfing
gungnir draupnir midgard jotun ullr vidar vali bragi idun forseti mimir norn skuld urd
verdandi kvasir hodr magni modi eir gefjun hlin sigyn ran aegir kari""".split()
OTHER = """polis fang radar abyss campaign shockbaton knife ballistic ballisticknife launcher""".split()

THEMES = {"ar": BIRDS, "sm": ANIMALS, "sh": DOGS, "sn": SEAS, "dm": SEAS, "pi": STARS,
          "me": STARS + OTHER, "lm": MYTH, "br": BIRDS + SEAS, "la": OTHER + MYTH}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--begins", type=int, default=400)
    ap.add_argument("--ends", type=int, default=3000)
    a = ap.parse_args()
    CONTRIB.mkdir(parents=True, exist_ok=True)
    codes = set()
    for cls, words in THEMES.items():
        for w in set(words):
            codes.add(f"{cls}_{w}")
            codes.add(f"{cls}_{w}exotic")
    known = (CONTRIB / "weapon_slot_weapons.txt").read_text(encoding="utf-8").split()
    codes |= {k + "exotic" for k in known if not k.endswith("exotic")}
    codes -= set(known)
    (CONTRIB / "themed_weapon_codes.txt").write_text("".join(c + "\n" for c in sorted(codes)),
                                                     encoding="utf-8")
    b = (CONTRIB / "weapon_slot_begins.txt").read_text(encoding="utf-8").splitlines()[:a.begins]
    e = (CONTRIB / "weapon_slot_ends.txt").read_text(encoding="utf-8").splitlines()[:a.ends]
    (CONTRIB / "themed_weapon_begins.txt").write_text("".join(x + "\n" for x in b), encoding="utf-8")
    (CONTRIB / "themed_weapon_ends.txt").write_text("".join(x + "\n" for x in e), encoding="utf-8")
    (CONTRIB / "themed_weapon.plan.txt").write_text(
        "label: themed weapon codenames -- guessed BO7 weapons through the weapon-slot plan\n"
        f"describe: {len(codes)} <class>_<word> codes from each class's codename theme (birds, animals, "
        f"dog breeds, seas, stars, myth) plus <known>exotic, x top {len(b)} beginnings / {len(e)} "
        "endings measured around known weapons; see contrib/themed_weapons.py\n"
        "begin: @contrib/themed_weapon_begins.txt\nstem: @contrib/themed_weapon_codes.txt\n"
        "end: @contrib/themed_weapon_ends.txt\n", encoding="utf-8")
    print(f"{len(codes)} codes, {len(b)} begins, {len(e)} ends")


if __name__ == "__main__":
    main()
