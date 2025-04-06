from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from openai import AsyncOpenAI
import tiktoken
import asyncio
from config import settings as st

client = AsyncOpenAI(api_key=st.OPENAI_API_KEY)


class AgentState(TypedDict):
    input_text: str
    chunks: List[str]
    partial_summaries: List[str]
    final_summary: str


def split_text(text: str, max_tokens=1500, model_name="gpt-3.5-turbo") -> List[str]:
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = encoding.decode(tokens[start:end])
        chunks.append(chunk)
        start = end

    return chunks


async def chunk_text(state: AgentState) -> AgentState:
    chunks = split_text(state["input_text"])
    return {**state, "chunks": chunks}


async def summarize_chunks(state: AgentState) -> AgentState:
    summaries = []

    async def summarize_chunk(chunk: str) -> str:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes concise summaries.",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following text:\n\n{chunk}",
                },
            ],
        )
        return response.choices[0].message.content.strip()

    # Run in parallel for speed
    summaries = await asyncio.gather(
        *(summarize_chunk(chunk) for chunk in state["chunks"])
    )

    return {**state, "partial_summaries": summaries}


async def final_summarize(state: AgentState) -> AgentState:
    combined = "\n\n".join(state["partial_summaries"])
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You generate a final, high-level summary."},
            {
                "role": "user",
                "content": f"Create a concise final summary based on these partial summaries:\n\n{combined}",
            },
        ],
    )
    return {**state, "final_summary": response.choices[0].message.content.strip()}


# -- Graph definition
graph_builder = StateGraph(AgentState)

graph_builder.add_node("chunk_text", chunk_text)
graph_builder.add_node("summarize_chunks", summarize_chunks)
graph_builder.add_node("final_summarize", final_summarize)

graph_builder.set_entry_point("chunk_text")
graph_builder.add_edge("chunk_text", "summarize_chunks")
graph_builder.add_edge("summarize_chunks", "final_summarize")
graph_builder.add_edge("final_summarize", END)

graph = graph_builder.compile()


async def summarize_long_text(text: str) -> str:
    result = await graph.ainvoke({"input_text": text})
    return result["final_summary"]


# if __name__ == "__main__":
#     text = """In the early 21st century, the landscape of technology began to shift at an unprecedented pace. As smartphones entered the pockets of billions, the very concept of "being connected" transformed. Gone were the days when the internet was accessed only through desktop computers tethered to walls. The emergence of cloud computing, mobile broadband, and increasingly powerful handheld devices meant that information could be accessed, shared, and manipulated on the go.
#
# Social media platforms like Facebook, Twitter, and later Instagram and TikTok reshaped the way humans interacted. While these platforms were initially celebrated for reconnecting old friends and amplifying voices across the world, their influence quickly drew scrutiny. Allegations of privacy violations, political manipulation, and mental health consequences sparked global debates. Governments began intervening, demanding transparency and regulation.
#
# Around the same time, artificial intelligence began moving from academic theory to commercial reality. In industries from logistics to healthcare, AI started optimizing processes, predicting outcomes, and in some cases, even making decisions. Machine learning models were trained on vast data sets, often without explicit user consent, raising ethical and legal concerns. But the promise was undeniable: improved diagnostics in medicine, more efficient supply chains, smarter recommendation engines, and even self-driving cars.
#
# By the mid-2020s, natural disasters intensified due to climate change. Wildfires in Australia and California raged longer than ever before. Floods in Europe displaced thousands. Heatwaves shattered records across continents. Climate models, powered by AI, became essential tools for governments and scientists alike. Despite clear warnings, political action remained slow. However, grassroots movements led by youth activists surged, demanding accountability and systemic change. Renewable energy investments grew, though not fast enough to offset the continued reliance on fossil fuels.
#
# The COVID-19 pandemic, which emerged in late 2019, accelerated digital transformation globally. Remote work, once a perk for a few, became the norm for millions. Zoom calls replaced conference rooms, and digital collaboration tools became vital. Schools transitioned online, highlighting massive inequities in digital access. The pandemic also exposed the fragility of global supply chains and healthcare systems, prompting countries to rethink resilience and self-sufficiency.
#
# In space, private companies like SpaceX and Blue Origin took over where national agencies had dominated. Space tourism became a reality for the ultra-wealthy. Missions to Mars were announced. Satellites blanketed Earth, providing internet to even the most remote regions. This commercialization of space raised concerns about space debris, monopolization of orbital lanes, and the weaponization of the final frontier.
#
# Meanwhile, the world grappled with a rising tide of misinformation. Deepfakes, algorithmically generated text, and social media echo chambers made it increasingly difficult to discern truth. Journalistic institutions struggled to adapt. Fact-checking became a full-time job. Algorithms, originally designed to optimize for engagement, began influencing public opinion in unpredictable and often dangerous ways.
#
# Amidst these challenges, breakthroughs emerged. Fusion energy made a surprising leap forward. Scientists reported more sustained reactions, sparking hope for a near-limitless energy future. Biotech firms developed CRISPR-based therapies that cured rare genetic disorders. Language models became so advanced that they could write essays, generate code, and even simulate conversation with humans convincingly. Ethical debates swirled: should these models be regulated, given their potential to mislead and manipulate?
#
# As the 2030s approached, the lines between the digital and physical world blurred further. Augmented reality glasses replaced smartphones in many urban settings. People interacted with digital overlays seamlessly in their daily lives — ordering food, navigating cities, or collaborating with colleagues. The metaverse, a persistent digital universe, gained traction as both a workplace and social hub. Questions of identity, privacy, and ownership in these virtual realms dominated legal and philosophical discourse.
#
# Education, too, was transformed. Personalized AI tutors adapted to each student's pace and style, dramatically improving learning outcomes in some regions. Yet digital divides persisted, and not all communities reaped the benefits equally. Teachers began shifting from lecturers to facilitators, guiding students in a world where information was abundant but context was rare.
#
# Economically, automation disrupted countless industries. Routine tasks were increasingly performed by machines, from warehouse sorting to legal document review. Universal Basic Income (UBI) trials expanded as a response to displacement. Some nations found success with hybrid models that blended UBI with upskilling programs. Others struggled with political resistance and budgetary constraints.
#
# Amid all this, the human spirit endured. Art, music, literature — though increasingly co-created with machines — continued to flourish. People still sought meaning, connection, and joy in shared experiences. The pace of change was dizzying, but so too was the capacity for adaptation.
#
# As humanity stood on the cusp of mid-century, one question echoed louder than others: how can technology serve the collective good without compromising the values that make us human? The answer remained elusive, but the pursuit itself was worth everything."""
#     result = asyncio.run(summarize_long_text(text))
#     print(result)
