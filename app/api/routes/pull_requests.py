from fastapi import APIRouter, status

from app.services.pull_requests.pull_requests_service import PullRequestService
from app.services.pull_requests.schemas import (
    PullRequestCreate,
    PullRequestMerge,
    PullRequestReassign,
    PullRequestResponse,
    PullRequestReassignResponse,
)

router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])


@router.post(
    "/create",
    response_model=PullRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать pull request",
)
async def create_pull_request(payload: PullRequestCreate) -> PullRequestResponse:
    pr = await PullRequestService.create_pull_request(payload)
    return PullRequestResponse(pr=await PullRequestService.to_dto(pr))


@router.post(
    "/merge",
    response_model=PullRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Смержить pull request",
)
async def merge_pull_request(payload: PullRequestMerge) -> PullRequestResponse:
    pr = await PullRequestService.merge_pull_request(payload.pull_request_id)
    return PullRequestResponse(pr=await PullRequestService.to_dto(pr))


@router.post(
    "/reassign",
    response_model=PullRequestReassignResponse,
    status_code=status.HTTP_200_OK,
    summary="Переназначить ревьювера",
)
async def reassign_pull_request(
    payload: PullRequestReassign,
) -> PullRequestReassignResponse:
    pr, replaced_by = await PullRequestService.reassign_pull_request(
        payload.pull_request_id, payload
    )
    return PullRequestReassignResponse(
        pr=await PullRequestService.to_dto(pr), replaced_by=replaced_by
    )
