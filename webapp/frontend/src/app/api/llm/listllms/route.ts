import {getListOfLLMs} from "@/lib/database";
import {NextResponse} from "next/server";

export async function GET() {
    try {
        const llmList = await getListOfLLMs();
        return NextResponse.json(llmList);
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch LLM list" }, { status: 500 });
    }
}
