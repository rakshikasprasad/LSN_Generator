from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
import re
app = Flask(__name__)

# Register Unicode-compatible font (Ensure 'NotoSans-Regular.ttf' is in the directory)
pdfmetrics.registerFont(TTFont("NotoSans", "NotoSans-Regular.ttf"))


# Dictionary mapping aspects of life to their corresponding mantra
# Clean and structure the extracted text into a dictionary

samputeekarana_map = {
    "Balancing of Spirituality and Mundane life": "aṣṭāmi candra vibhāṛāja daḷjikasthala śobhitā (5-1)",
    "For Attractive speech": "karpūrāvāṭi kāmoda samākarṣa digdantarā (10-2)",
    "For Good musical voice": "nijasallāpa mādhurya vinirbhart-sīta kacchapī (11-2)",
    "For girls getting marriage": "kāmeśabaddha māṅgalyā sūtrāśobhita kantharā (12-1)",
    "Winning husband's love with your feminine character": "kāmeśvara premaratna maṇi pratipānasthitī (14-1)",
    "Reducing Knee pain": "māṇikya-mukuṭākāra-jānudvaya-virājitā (17-2)",
    "Reducing Pain in calf muscle": "indragopa parikṣipta smara tūnābha jaṅghikā (18-1)",
    "For graceful walk and internal beauty": "marālī mandagamana, mahāla vāṇya śevadhih (20-2)",
    "For inner and external beauty": "sarvāruṇa navadyāyī sarvābharaṇa bhūṣitā (21-1)",
    "For fulfilment of reasonable desires": "cintāmaṇi gṛhāntasthā, pañcabraḥmāsanasthitā (22-1)",
    "Chakra awakening": "mahāpadmāṭavī saṃsthā, kadamba vanavāsinī (23-4)",
    "Removal of inner enemies": "devarṣi gaṇasaṅghāta stuyamānātmana vaibhavā (24-1)",
    "For live energy": "bhāṇḍaputra vadhodyukta balavikrama nanditā (29-4)",
    "For effective planning": "geyayacara rathārūḍhā mantriṇī parisevitā (26-2)",
    "For tackling impotency and depression": "viśukra prāṇa-haraṇā vārāhī vīryananditā (30-1)",
    "For conceiving children": "kāmeśvara mukhāloka kalpita śrī gaṇeśvarā (30-2)",
    "Removal of black magic": "brahmopendra mahendrādi devasamsatuta vaibhavā (33-2)",
    "For auspicious fame": "rājarājārcitā, rāmā, ramyā, rājīvallabā (111-1)",
    "Removal of negative energy in and out": "duṣṭagrahā, dūracāra śamanī, doṣavārjitā (51-1)",
    "For all-round auspiciousness": "sarvāsaṅga-parityāginī, sarvānanda pradayinī (62-1)",
    "For Job and business": "maheśvarī, mahādevī, mahālakṣmī, mahāprajñā (63-2)",
    "For oneness with world": "rākṣasārī, rakṣasa-ghnī, rāmā, rāmālaṅkṛtā (72-2)",
    "For detachment": "saṃśārāpāṅka nirmagnā samuddharaṇa paṇḍitā (164-1)",
    "For inner peace": "svātmānandalavibhūta brahmādyānanda santatiḥ (80-2)",
    "For removal of frigidity in women": "śṛṅgāra rasasaṃpūrṇā, jayā, jālandharasthitā (82-2)",
    "For Gynic problem": "nityaklinna, nirupamā, nirvāṇa sukhadāyinī (87-1)",
    "Communication and managerial skills": "śivadūtī, śivārādhyā, śivamūrti, śivakarī (88-2)",
    "Good thoughts and enjoying peace": "śāntiḥ, śvastimati, kānti, mandinī, vighnanāśinī (94-2)",
    "For Skin decease": "pāyasānna priya tvaṣṭhaka pasuloka bhayankare (95-1)",
    "For Blood deceases": "daṃṣṭrojvalā, kṣamālādhāradhā, rudhira saṃsthita (97-1)",
    "For muscular problems": "raktavarnā, māṃsaṅgāsthita, guṇadna pṛthamaṅgāśa (98-1)",
    "For intellectual ability or handling autism": "medonishṭhā, madhupṛitā, bandinyādhi samanvitā (103-1)",
    "For removing back pain": "mūlādhārām bujārūḍhā pañca-vaktrā’sthi-saṃsthita (106-1)",
    "For bone marrow problems": "majjāsaṃsthā, haṃsāvātī mukhyasakti samanvitā (108-1)",
    "For sperm count": "sarvāyudhadhārā, śukla saṃsthita, sarvātmikā (109-1)",
    "Food allergy": "sarvadāna pṛticattā, yākyinymabā sarvāpini (110-1)",
    "Self-analysis": "vimarśarūpiṇī, vidyā, vijayād jagatprasūḥ (112-1)",
    "For Contentment": "nityatṛptā, bhaktānidhi, nityanītī, nikhilesvarī (115-1)",
    "Removal of depression": "hṛdayasthā, raviprakhyā, trikoṇātara dīpikā (127-2)",
    "Focus in meditation": "dhyānagamyā, aparicchedyā, nirādhā, nānāvigarāhā (127-2)",
    "For achieving internal independency by coming out of external dependency": "sarvopādhi vinirmuktā, sadāśiva pativratā (138-1)",
    "Terminal illness": "prāṇeśvarī, prāṇadātrī, pañcaśat-pīṭharūpiṇī (156-1)"
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

def generate_pdf(selected_aspect, samputeekarana):
    """
    Generate a PDF named after the selected aspect.
    """
    # Create a safe filename from the selected aspect
    safe_filename = re.sub(r"[^a-zA-Z0-9\s]", "", selected_aspect).replace(" ", "_") + ".pdf"

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("NotoSans", 12)
    y = 800  # Initial positioning in the PDF

    for line in sahasranama_lines:
        pdf.drawString(100, y, samputeekarana)
        y -= 20
        pdf.drawString(100, y, line.strip())
        y -= 20
        pdf.drawString(100, y, samputeekarana)
        y -= 40

        if y < 50:
            pdf.showPage()
            pdf.setFont("NotoSans", 12)
            y = 800

    pdf.save()
    buffer.seek(0)

    return buffer, safe_filename

if __name__ == "__main__":
    app.run(debug=True)