import streamlit as st
from core.models import Proposal, TraceID, VerdictStatus
from gate.gate import Gate
from gate.validator import GateValidator

st.set_page_config(page_title="AMALIA Demo", page_icon="🧠", layout="wide")

st.title("🧠 AMALIA-NeSyOps Demo")
st.markdown("### Neuro-symbolic middleware for auditable administrative decisions")

st.sidebar.header("⚙️ Configuration")
pilot_mode = st.sidebar.checkbox("Pilot Mode (Human Review)", value=False)

st.markdown("---")
st.subheader("📝 Submit a Proposal")

document_text = st.text_area(
    "Document Text (Portuguese)",
    value="Requerimento de licença comercial para restaurante no centro da cidade.",
    height=100
)

age = st.number_input("Applicant Age", min_value=0, max_value=120, value=25)
area_m2 = st.number_input("Establishment Area (m²)", min_value=0, value=50)

if st.button("🔍 Process Decision", type="primary"):
    with st.spinner("Evaluating..."):
        gate = Gate(GateValidator())
        
        p = Proposal(
            trace_id=TraceID(),
            agent="demo-ui",
            content={
                "document_text": document_text,
                "age": age,
                "area_m2": area_m2
            },
            confidence=0.95
        )
        
        result = gate.evaluate(p)
        verdict = result["verdict"].status
        
        st.markdown("---")
        st.subheader("📊 Decision Result")
        
        if verdict == VerdictStatus.APPROVED:
            st.success("✅ APPROVED")
        elif verdict == VerdictStatus.REJECTED:
            st.error("❌ REJECTED")
        else:
            st.warning("⚠️ PENDING REVIEW")
        
        st.markdown("**Explanation:**")
        st.json(result.get("explanation", {}))
        
        if pilot_mode:
            st.info("👤 Pilot Mode active: Decision routed to human review queue.")
