import httpx
from fastapi import HTTPException, status


class ArtInstituteClient:
    BASE_URL = "https://api.artic.edu/api/v1/artworks"

    @classmethod
    async def validate_artwork(cls, artwork_id: int) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{cls.BASE_URL}/{artwork_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return True
                if 400 <= response.status_code < 500:
                    return False
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Art Institute API returned an unexpected error."
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="External Art Institute API is unavailable."
                )
