#! /usr/bin/env -S python3 -B

"""Write example QR codes."""

import subprocess

from sources.qrcode_generator.data_encoder import DataEncoder
from sources.qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from sources.qrcode_generator.qr_code import make_qr_code
from sources.qrcode_generator.render_pil import render_qrcode_as_pil_image
from sources.qrcode_generator.utilities import write_optimal_qrcode

pi_10k = (
    "3."
    "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
    "8214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
    "4428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273"
    "7245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094"
    "3305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912"
    "9833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132"
    "0005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235"
    "4201995611212902196086403441815981362977477130996051870721134999999837297804995105973173281609631859"
    "5024459455346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303"
    "5982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"
    "3809525720106548586327886593615338182796823030195203530185296899577362259941389124972177528347913151"
    "5574857242454150695950829533116861727855889075098381754637464939319255060400927701671139009848824012"
    "8583616035637076601047101819429555961989467678374494482553797747268471040475346462080466842590694912"
    "9331367702898915210475216205696602405803815019351125338243003558764024749647326391419927260426992279"
    "6782354781636009341721641219924586315030286182974555706749838505494588586926995690927210797509302955"
    "3211653449872027559602364806654991198818347977535663698074265425278625518184175746728909777727938000"
    "8164706001614524919217321721477235014144197356854816136115735255213347574184946843852332390739414333"
    "4547762416862518983569485562099219222184272550254256887671790494601653466804988627232791786085784383"
    "8279679766814541009538837863609506800642251252051173929848960841284886269456042419652850222106611863"
    "0674427862203919494504712371378696095636437191728746776465757396241389086583264599581339047802759009"
    "9465764078951269468398352595709825822620522489407726719478268482601476990902640136394437455305068203"
    "4962524517493996514314298091906592509372216964615157098583874105978859597729754989301617539284681382"
    "6868386894277415599185592524595395943104997252468084598727364469584865383673622262609912460805124388"
    "4390451244136549762780797715691435997700129616089441694868555848406353422072225828488648158456028506"
    "0168427394522674676788952521385225499546667278239864565961163548862305774564980355936345681743241125"
    "1507606947945109659609402522887971089314566913686722874894056010150330861792868092087476091782493858"
    "9009714909675985261365549781893129784821682998948722658804857564014270477555132379641451523746234364"
    "5428584447952658678210511413547357395231134271661021359695362314429524849371871101457654035902799344"
    "0374200731057853906219838744780847848968332144571386875194350643021845319104848100537061468067491927"
    "8191197939952061419663428754440643745123718192179998391015919561814675142691239748940907186494231961"
    "5679452080951465502252316038819301420937621378559566389377870830390697920773467221825625996615014215"
    "0306803844773454920260541466592520149744285073251866600213243408819071048633173464965145390579626856"
    "1005508106658796998163574736384052571459102897064140110971206280439039759515677157700420337869936007"
    "2305587631763594218731251471205329281918261861258673215791984148488291644706095752706957220917567116"
    "7229109816909152801735067127485832228718352093539657251210835791513698820914442100675103346711031412"
    "6711136990865851639831501970165151168517143765761835155650884909989859982387345528331635507647918535"
    "8932261854896321329330898570642046752590709154814165498594616371802709819943099244889575712828905923"
    "2332609729971208443357326548938239119325974636673058360414281388303203824903758985243744170291327656"
    "1809377344403070746921120191302033038019762110110044929321516084244485963766983895228684783123552658"
    "2131449576857262433441893039686426243410773226978028073189154411010446823252716201052652272111660396"
    "6655730925471105578537634668206531098965269186205647693125705863566201855810072936065987648611791045"
    "3348850346113657686753249441668039626579787718556084552965412665408530614344431858676975145661406800"
    "7002378776591344017127494704205622305389945613140711270004078547332699390814546646458807972708266830"
    "6343285878569830523580893306575740679545716377525420211495576158140025012622859413021647155097925923"
    "0990796547376125517656751357517829666454779174501129961489030463994713296210734043751895735961458901"
    "9389713111790429782856475032031986915140287080859904801094121472213179476477726224142548545403321571"
    "8530614228813758504306332175182979866223717215916077166925474873898665494945011465406284336639379003"
    "9769265672146385306736096571209180763832716641627488880078692560290228472104031721186082041900042296"
    "6171196377921337575114959501566049631862947265473642523081770367515906735023507283540567040386743513"
    "6222247715891504953098444893330963408780769325993978054193414473774418426312986080998886874132604721"
    "5695162396586457302163159819319516735381297416772947867242292465436680098067692823828068996400482435"
    "4037014163149658979409243237896907069779422362508221688957383798623001593776471651228935786015881617"
    "5578297352334460428151262720373431465319777741603199066554187639792933441952154134189948544473456738"
    "3162499341913181480927777103863877343177207545654532207770921201905166096280490926360197598828161332"
    "3166636528619326686336062735676303544776280350450777235547105859548702790814356240145171806246436267"
    "9456127531813407833033625423278394497538243720583531147711992606381334677687969597030983391307710987"
    "0408591337464144282277263465947047458784778720192771528073176790770715721344473060570073349243693113"
    "8350493163128404251219256517980694113528013147013047816437885185290928545201165839341965621349143415"
    "9562586586557055269049652098580338507224264829397285847831630577775606888764462482468579260395352773"
    "4803048029005876075825104747091643961362676044925627420420832085661190625454337213153595845068772460"
    "2901618766795240616342522577195429162991930645537799140373404328752628889639958794757291746426357455"
    "2540790914513571113694109119393251910760208252026187985318877058429725916778131496990090192116971737"
    "2784768472686084900337702424291651300500516832336435038951702989392233451722013812806965011784408745"
    "1960121228599371623130171144484640903890644954440061986907548516026327505298349187407866808818338510"
    "2283345085048608250393021332197155184306354550076682829493041377655279397517546139539846833936383047"
    "4611996653858153842056853386218672523340283087112328278921250771262946322956398989893582116745627010"
    "2183564622013496715188190973038119800497340723961036854066431939509790190699639552453005450580685501"
    "9567302292191393391856803449039820595510022635353619204199474553859381023439554495977837790237421617"
    "2711172364343543947822181852862408514006660443325888569867054315470696574745855033232334210730154594"
    "0516553790686627333799585115625784322988273723198987571415957811196358330059408730681216028764962867"
    "4460477464915995054973742562690104903778198683593814657412680492564879855614537234786733039046883834"
    "3634655379498641927056387293174872332083760112302991136793862708943879936201629515413371424892830722"
    "0126901475466847653576164773794675200490757155527819653621323926406160136358155907422020203187277605"
    "2772190055614842555187925303435139844253223415762336106425063904975008656271095359194658975141310348"
    "2276930624743536325691607815478181152843667957061108615331504452127473924544945423682886061340841486"
    "3776700961207151249140430272538607648236341433462351897576645216413767969031495019108575984423919862"
    "9164219399490723623464684411739403265918404437805133389452574239950829659122850855582157250310712570"
    "1266830240292952522011872676756220415420516184163484756516999811614101002996078386909291603028840026"
    "9104140792886215078424516709087000699282120660418371806535567252532567532861291042487761825829765157"
    "9598470356222629348600341587229805349896502262917487882027342092222453398562647669149055628425039127"
    "5771028402799806636582548892648802545661017296702664076559042909945681506526530537182941270336931378"
    "5178609040708667114965583434347693385781711386455873678123014587687126603489139095620099393610310291"
    "6161528813843790990423174733639480457593149314052976347574811935670911013775172100803155902485309066"
    "9203767192203322909433467685142214477379393751703443661991040337511173547191855046449026365512816228"
    "8244625759163330391072253837421821408835086573917715096828874782656995995744906617583441375223970968"
    "3408005355984917541738188399944697486762655165827658483588453142775687900290951702835297163445621296"
    "4043523117600665101241200659755851276178583829204197484423608007193045761893234922927965019875187212"
    "7267507981255470958904556357921221033346697499235630254947802490114195212382815309114079073860251522"
    "7429958180724716259166854513331239480494707911915326734302824418604142636395480004480026704962482017"
    "9289647669758318327131425170296923488962766844032326092752496035799646925650493681836090032380929345"
    "9588970695365349406034021665443755890045632882250545255640564482465151875471196218443965825337543885"
    "6909411303150952617937800297412076651479394259029896959469955657612186561967337862362561252163208628"
    "6922210327488921865436480229678070576561514463204692790682120738837781423356282360896320806822246801"
    "2248261177185896381409183903673672220888321513755600372798394004152970028783076670944474560134556417"
    "2543709069793961225714298946715435784687886144458123145935719849225284716050492212424701412147805734"
    "5510500801908699603302763478708108175450119307141223390866393833952942578690507643100638351983438934"
    "1596131854347546495569781038293097164651438407007073604112373599843452251610507027056235266012764848"
    "3084076118301305279320542746286540360367453286510570658748822569815793678976697422057505968344086973"
    "5020141020672358502007245225632651341055924019027421624843914035998953539459094407046912091409387001"
    "2645600162374288021092764579310657922955249887275846101264836999892256959688159205600101655256375678"
)


def write_example_kanji_encodings(s: str, filename: str, *, post_optimize: bool = False) -> None:
    """Represent Kanji characters as both UTF-8 and Kanji encoding.

    This routine is a bit verbose because it uses a DataEncoder with hand-picked encoding blocks.
    Normally we'd depend on the 'find_optimal_string_encoding' function instead (either directly
    or indirectly).
    """
    de = DataEncoder(EncodingVariant.SMALL)
    de.append_byte_mode_block("Kanji characters as Kanji mode block:\n\n".encode())
    de.append_kanji_mode_block(s)
    de.append_byte_mode_block(f"\n\nKanji characters as byte mode block with UTF-8 encoding:\n\n{s}".encode())
    qr_canvas = make_qr_code(de, 7, ErrorCorrectionLevel.L)
    im = render_qrcode_as_pil_image(qr_canvas)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        subprocess.run(["optipng", filename], stderr=subprocess.DEVNULL, check=False)


def main():

    # This produces a QR code with an empty string.
    write_optimal_qrcode("", "example_empty.png", post_optimize=True)

    # This produces a QR code with the snowman character (\u2603) from UTF-8, written in a "bytes" block.
    write_optimal_qrcode("☃", "example_utf8_snowman.png", post_optimize=True)

    # A simple example that uses a single Kanji block.
    # The Kanji text says: "I don't understand Japanese."
    write_optimal_qrcode("日本語はわかりません。", "example_kanji.png", post_optimize=True)

    # An example where the same Kanji text is first rendered in Kanji mode, then later on in
    # UTF-8 mode. The Kanji text says: "I don't understand Japanese."
    write_example_kanji_encodings("日本語はわかりません。", "example_kanji_encodings.png", post_optimize=True)

    # This example reproduces the QR code of Appendix I of the standard.
    write_optimal_qrcode("01234567", "example_appendix_i.png",
                         pattern=DataMaskingPattern.Pattern2,
                         version_preference_list=[(1, ErrorCorrectionLevel.M)], post_optimize=True)

    # The most digits of Pi that can be stored into a QR code;
    # "3." followed by 7080 digits after the decimal point.
    write_optimal_qrcode(pi_10k[:7082], "example_pi_digits.png",
                         version_preference_list=[(40, ErrorCorrectionLevel.L)], post_optimize=True)

    # A simple URL.
    write_optimal_qrcode("http://www.google.com/", "example_url.png", post_optimize=True)

    # A geolocation URL (RFC 5870).
    write_optimal_qrcode("geo:52.000000,4.000000", "example_geolocation.png", post_optimize=True)

    # A mailto URL (RFC 6068).
    write_optimal_qrcode("mailto:sidney@jigsaw.nl", "example_mailto.png", post_optimize=True)

    # Some more examples may be added:
    # - vcard
    # - phone
    # - email
    # - sms
    # - Wi-Fi
    # - event
    # - embedded HTML (even though it's not supported).


if __name__ == "__main__":
    main()
