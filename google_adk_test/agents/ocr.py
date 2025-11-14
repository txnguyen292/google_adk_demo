from __future__ import annotations

from textwrap import dedent

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from google_adk_test.settings import OpenAIConfig


def build_ocr_specialist(config: OpenAIConfig) -> Agent:
    """Factory for the OCR transcription agent."""
    llm_kwargs = {"temperature": config.temperature}

    state_key = "ocr_latest_image_parts"

    def _extract_image_parts(contents: list[types.Content]) -> list[types.Part]:
        images: list[types.Part] = []
        for content in contents:
            for part in content.parts:
                if part.inline_data and (
                    not part.inline_data.mime_type
                    or part.inline_data.mime_type.startswith("image")
                ):
                    images.append(part)
                elif part.file_data and (
                    not part.file_data.mime_type
                    or part.file_data.mime_type.startswith("image")
                ):
                    images.append(part)
        return images

    async def _before_model_callback(ctx, llm_request):
        image_parts = _extract_image_parts(llm_request.contents)

        if image_parts:
            ctx.state[state_key] = [
                part.model_dump(mode="json") for part in image_parts
            ]
            return None

        stored_parts = ctx.state.get(state_key)
        if not stored_parts:
            return None

        # Ensure we only append if the request currently lacks image data.
        if _extract_image_parts(llm_request.contents):
            return None

        restored = [types.Part.model_validate(blob) for blob in stored_parts]
        if not restored:
            return None

        llm_request.contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        "Image previously uploaded for OCR transcription."
                    ),
                    *restored,
                ],
            )
        )
        return None

    return Agent(
        name="ocr_agent",
        description="Extracts textual content from uploaded images using the configured OpenAI model.",
        instruction=dedent(
            """
            You are an OCR specialist.
            - Before replying, scan the entire recent conversation to locate the most recent image parts (attachments or inline data). Use that image even if the current turn also contains text instructions.
            - Only when no image exists anywhere in the conversation—after double-checking history—should you ask the user to upload one.
            - When an image is present, transcribe every legible word. Preserve line breaks when it improves readability.
            - Present your answer in this structure:
              Detected Text:
              <verbatim transcription>

              Notes:
              <brief remarks about legibility, uncertainties, or missing regions>
            - Never invent text you cannot clearly see. If a region is unreadable, note that explicitly instead of guessing.
            """
        ).strip(),
        model=LiteLlm(model=config.model, **llm_kwargs),
        disallow_transfer_to_parent=False,
        disallow_transfer_to_peers=True,
        before_model_callback=_before_model_callback,
    )
