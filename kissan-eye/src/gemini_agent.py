import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from src.vertex_config import init_vertex

class KissanAgent:
    def __init__(self, pdf_context: str):
        """
        Initializes KissanAgent using Vertex AI (service account auth).
        """
        init_vertex()
        self.pdf_context = pdf_context
        self.model = GenerativeModel(
            model_name="gemini-1.5-flash-001",
            system_instruction=["""
                Tu ek expert KP kisano ka AI sahayak hai — Kissan-Eye.
                Apne jawab SIRF Roman Urdu mein do.
                Diye gaye PDF content ko apni knowledge base mano.
                Agar PDF mein jawab nahi hai to kaho: 'Is baare mein mujhe yaqeen nahi.'
                Format:
                 Bimari/Masla: [naam]
                 Alamaat: [kya dikh raha hai]
                 Ilaj: [kya karna chahiye]
                ⚠️ Ehtiyat: [kya nahi karna]
            """]
        )

    def diagnose(self, image_bytes: bytes, user_description: str) -> str:
        """
        Diagnoses crop disease from image bytes and user description via Vertex AI.
        """
        image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
        prompt = f"""
            PDF Knowledge Base:
            {self.pdf_context}

            Kisan ka masla: {user_description}
            
            ZAROORI: Apna jawab PLAIN TEXT mein do.
            Koi markdown mat use karo — koi ** ya ## ya --- nahi.
            Sirf saaf Roman Urdu mein likho jaise koi insaan likhta hai.

            Is tasweer mein fasal ki bimari diagnose karo.
        """
        response = self.model.generate_content([prompt, image_part])
        return response.text

    def find_resource_center(self, disease_name: str) -> str:
        """
        SIMULATED — replace with Maps API
        Returns a hardcoded simulated response in Roman Urdu listing 3 fictional KP resource centers.
        """
        # SIMULATED — replace with Maps API
        simulated_response = (
            f"Aap ki fasal mein '{disease_name}' ke liye ye qareebi resource centers hain:\n\n"
            "1. KP Model Seed Center - Peshawar\n"
            "   Pata: GT Road, Qissa Khwani Bazar ke qareeb\n"
            "   Phone: 091-555-0101\n\n"
            "2. Abasin Zara-ee Markaz - Mardan\n"
            "   Pata: Swabi Road, Industrial Estate\n"
            "   Phone: 0937-555-0202\n\n"
            "3. Malakand Agri-Hub - Mingora\n"
            "   Pata: Bypass Road, Saidu Sharif\n"
            "   Phone: 0946-555-0303\n\n"
            "In centers se aap ko sasti khad aur dawai mil sakti hai."
        )
        return simulated_response
