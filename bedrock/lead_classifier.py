import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from bedrock.bedrock_process import call_bedrock_structured
from config.models import ClassificationResponse

async def classify_business_lead(news_text: str) -> str:
    system_role = """
<System>
    <Role>You are an expert Sales Development Analyst with a focus on identifying ANY potential B2B sales opportunities. Your approach is to be INCLUSIVE rather than exclusive when identifying leads.</Role>
    <Task>Extract all relevant information strictly based on the content of the article. When in doubt about lead potential, ALWAYS lean towards accepting as a lead rather than rejecting.</Task>
    <OutputFormat>Return a single, clean JSON object that strictly conforms to the provided schema. If a field's value is not found, use null.</OutputFormat>
</System>
"""

    prompt = f"""
<CriticalReminder>
**NEVER REJECT these as non-leads:**
    - CSR initiatives, sustainability programs, or environmental commitments (these require vendors/consultants)
    - Policy updates or compliance changes (companies need implementation support)
    - Any mention of spending, investments, or budget allocations
    - Industry trends that mention specific companies
    - Regulatory changes affecting businesses
    - Company statements about future plans or adaptations
</CriticalReminder>


<LeadRejectionCriteria>
    **CRITICAL**: Only reject an article if it EXCLUSIVELY focuses on:
    - Pure crime reports with no business implications
    - Celebrity personal life/gossip with no business context
    - Pure sports scores/results with no business angles
    - Obituaries with no business succession/impact mentioned
    - Natural disasters with no business recovery/impact discussed
    
    **IMPORTANT**: If ANY business element is present, even minimally, treat as a potential lead.
</LeadRejectionCriteria>

<LeadAcceptanceCriteria>
    **ACCEPT AS LEAD if the article mentions ANY of the following (even briefly):**
    
    **Direct Business Opportunities:**
    - New products, services, or business launches
    - Funding, investments, IPOs, or financial backing
    - Partnerships, joint ventures, or collaborations
    - Mergers, acquisitions, or corporate restructuring
    - New contracts, deals, or client wins
    - Market expansion or new location openings
    - Technology implementations or digital transformations
    
    **Growth & Change Indicators:**
    - Revenue growth, profit increases, or business expansion
    - New hiring, team expansion, or organizational changes
    - Leadership changes (new executives, board members)
    - Industry awards, certifications, or recognition
    - Research breakthroughs or innovation announcements
    
    **Market Position & Strategy:**
    - Competitive positioning or market share gains
    - Strategic pivots or business model changes
    - Regulatory approvals or compliance achievements
    - Sustainability initiatives or ESG commitments
    - Industry analysis with company-specific insights
    
    **Operational Changes:**
    - Infrastructure development or facility expansions
    - Supply chain modifications or vendor changes
    - Process improvements or efficiency gains
    - Cost reduction initiatives or restructuring
    - Customer base expansion or new market entry
    
    **Even Subtle Indicators:**
    - Company mentioned in industry trend discussions
    - Quoted executives discussing business strategy
    - Companies responding to market challenges
    - Participation in industry events or conferences
    - Any mention of business pain points or needs
    - Companies adapting to new regulations or market conditions
</LeadAcceptanceCriteria>

<Instructions>
    
    1.  **Default to Lead**: Start with the assumption that this COULD not be a lead unless it clearly falls into acceptance criteria.
    2.  **Look for ANY Business Angle**: Even if the primary focus isn't business, look for any business implications, company mentions, or commercial angles.
    3.  **Set the 'label' field**:
        - Set `label` to "NOT LEAD" only if the article has ZERO business relevance and clearly falls into the LeadRejectionCriteria.
        - If there is ANY doubt or any business element is present, set `label` to "LEAD".
    4.  **Be Conservative with Rejections**: Only label as "NOT LEAD" if you are absolutely certain there is no business angle.
    5.  **Extract All Possible Data**: If the label is "LEAD", extract every piece of information that could be remotely relevant to B2B sales.
    6.  **When in Doubt, Include**: If you're uncertain whether something qualifies as a lead, ALWAYS classify it as a lead rather than risk missing an opportunity.
</Instructions>

<Article>
{news_text}
</Article>
"""

    try:
        result = await call_bedrock_structured(system_role, prompt, ClassificationResponse)
    except Exception as e:
        return "ERROR"

    label = None
    if result and hasattr(result, "label"):
        label = result.label
    elif isinstance(result, dict) and "label" in result:
        label = result["label"]
    else:
        label = "NOT LEAD"
    return label
