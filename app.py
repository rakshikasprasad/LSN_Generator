from flask import Flask, render_template, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
import io
import re



app = Flask(__name__)

# Register Unicode-compatible font (Ensure 'NotoSans-Regular.ttf' is in the directory)
pdfmetrics.registerFont(TTFont("NotoSans", "NotoSans-Regular.ttf"))


# Dictionary mapping aspects of life to their corresponding mantra
# Clean and structure the extracted text into a dictionary

samputeekarana_map = {
    "Balancing of Spirituality and Mundane life": "aṣṭāmi candra vibhāṛāja daḷjikasthala śobhitā",
    "For Attractive speech": "karpūrāvāṭi kāmoda samākarṣa digdantarā",
    "For Good musical voice": "nijasallāpa mādhurya vinirbhart-sīta kacchapī",
    "For girls getting marriage": "kāmeśabaddha māṅgalyā sūtrāśobhita kantharā",
    "Winning husband's love with your feminine character": "kāmeśvara premaratna maṇi pratipānasthitī",
    "Reducing Knee pain": "māṇikya-mukuṭākāra-jānudvaya-virājitā",
    "Reducing Pain in calf muscle": "indragopa parikṣipta smara tūnābha jaṅghikā",
    "For graceful walk and internal beauty": "marālī mandagamana, mahāla vāṇya śevadhih",
    "For inner and external beauty": "sarvāruṇa navadyāyī sarvābharaṇa bhūṣitā",
    "For fulfilment of reasonable desires": "cintāmaṇi gṛhāntasthā, pañcabraḥmāsanasthitā",
    "Chakra awakening": "mahāpadmāṭavī saṃsthā, kadamba vanavāsinī",
    "Removal of inner enemies": "devarṣi gaṇasaṅghāta stuyamānātmana vaibhavā",
    "For live energy": "bhāṇḍaputra vadhodyukta balavikrama nanditā",
    "For effective planning": "geyayacara rathārūḍhā mantriṇī parisevitā",
    "For tackling impotency and depression": "viśukra prāṇa-haraṇā vārāhī vīryananditā",
    "For conceiving children": "kāmeśvara mukhāloka kalpita śrī gaṇeśvarā",
    "Removal of black magic": "brahmopendra mahendrādi devasamsatuta vaibhavā",
    "For auspicious fame": "rājarājārcitā, rāmā, ramyā, rājīvallabā",
    "Removal of negative energy in and out": "duṣṭagrahā, dūracāra śamanī, doṣavārjitā",
    "For all-round auspiciousness": "sarvāsaṅga-parityāginī, sarvānanda pradayinī",
    "For Job and business": "maheśvarī, mahādevī, mahālakṣmī, mahāprajñā",
    "For oneness with world": "rākṣasārī, rakṣasa-ghnī, rāmā, rāmālaṅkṛtā",
    "For detachment": "saṃśārāpāṅka nirmagnā samuddharaṇa paṇḍitā",
    "For inner peace": "svātmānandalavibhūta brahmādyānanda santatiḥ",
    "For removal of frigidity in women": "śṛṅgāra rasasaṃpūrṇā, jayā, jālandharasthitā",
    "For Gynic problem": "nityaklinna, nirupamā, nirvāṇa sukhadāyinī",
    "Communication and managerial skills": "śivadūtī, śivārādhyā, śivamūrti, śivakarī",
    "Good thoughts and enjoying peace": "śāntiḥ, śvastimati, kānti, mandinī, vighnanāśinī",
    "For Skin disease": "pāyasānna priya tvaṣṭhaka pasuloka bhayankare",
    "For Blood diseases": "daṃṣṭrojvalā, kṣamālādhāradhā, rudhira saṃsthita",
    "For muscular problems": "raktavarnā, māṃsaṅgāsthita, guṇadna pṛthamaṅgāśa",
    "For intellectual ability or handling autism": "medonishṭhā, madhupṛitā, bandinyādhi samanvitā",
    "For removing back pain": "mūlādhārām bujārūḍhā pañca-vaktrā’sthi-saṃsthita",
    "For bone marrow problems": "majjāsaṃsthā, haṃsāvātī mukhyasakti samanvitā",
    "For sperm count": "sarvāyudhadhārā, śukla saṃsthita, sarvātmikā",
    "Food allergy": "sarvadāna pṛticattā, yākyinymabā sarvāpini",
    "Self-analysis": "vimarśarūpiṇī, vidyā, vijayād jagatprasūḥ",
    "For Contentment": "nityatṛptā, bhaktānidhi, nityanītī, nikhilesvarī",
    "Removal of depression": "hṛdayasthā, raviprakhyā, trikoṇātara dīpikā",
    "Focus in meditation": "dhyānagamyā, aparicchedyā, nirādhā, nānāvigarāhā",
    "For achieving internal independence by coming out of external dependency": "sarvopādhi vinirmuktā, sadāśiva pativratā",
    "Terminal illness": "prāṇeśvarī, prāṇadātrī, pañcaśat-pīṭharūpiṇī"
}
def load_lalitha_sahasranama():
    with open("lalitha_sahasranama.txt", "r", encoding="utf-8") as file:
        return file.readlines()

sahasranama_lines = load_lalitha_sahasranama()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_aspect = request.form["aspect"]
        samputeekarana = samputeekarana_map.get(selected_aspect, "Mantra not found")

        # Generate PDF with filename based on selected aspect
        pdf_buffer, pdf_filename = generate_pdf(selected_aspect, samputeekarana)

        return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name=pdf_filename)

    return render_template("index.html", aspects=samputeekarana_map.keys())

@app.route("/get-mantra", methods=["POST"])
def get_mantra():
    """Fetch the Samputeekarana mantra dynamically."""
    try:
        data = request.get_json()  # Get JSON data
        selected_aspect = data.get("aspect")  # Extract 'aspect' from request

        if not selected_aspect:
            return jsonify({"mantra": "Aspect not provided"}), 400

        mantra = samputeekarana_map.get(selected_aspect, "Mantra not found")
        return jsonify({"mantra": mantra})
    except Exception as e:
        return jsonify({"mantra": "Error processing request", "error": str(e)}), 500

def generate_pdf(selected_aspect, samputeekarana):
    """
    Generate a PDF with a centered header and footer.
    """
    safe_filename = "Samputeekarana_LSN_" + re.sub(r"[^a-zA-Z0-9\s]", "", selected_aspect).replace(" ", "_") + ".pdf"
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    
    def add_header_footer():
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(width / 2, height - 30, "Sree Matre Namaha")
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(width / 2, height - 50, "Sri Vidya Learning Center, Kanchipuram")

        # Footer section
        pdf.setFont("Helvetica", 9)
        
    # Center-aligned: Website & Facebook
        pdf.drawString(50, 40, "www.srimeru.org")
        pdf.drawString(50, 60, "www.facebook.com/Soundarya.Lahari")
        
        # Right-aligned: Contact Info
        pdf.drawRightString(width - 50, 40, "8088256632, 8867709990")
        pdf.drawRightString(width - 50, 60, "srimeru999@gmail.com")

    pdf.setFont("NotoSans", 12)
    y = height - 80  # Start below the header

    for line in sahasranama_lines:
        if y < 50:
            add_header_footer()
            pdf.showPage()
            pdf.setFont("NotoSans", 12)
            y = height - 80

        pdf.drawString(100, y, samputeekarana)
        y -= 20
        pdf.drawString(100, y, line.strip())
        y -= 20
        pdf.drawString(100, y, samputeekarana)
        y -= 40

    add_header_footer()  # Ensure footer is added before saving
    pdf.save()
    buffer.seek(0)

    return buffer, safe_filename


if __name__ == "__main__":
    app.run(debug=True)
