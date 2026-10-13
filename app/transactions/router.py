from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.transactions.schema import (
    DailyNetTotalResponse,
    TransactionCreateRequest,
    TransactionDetailResponse,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdateRequest,
)
from app.transactions.service import (
    create_transaction,
    get_transactions,
    get_daily_net_totals,
    get_transaction_detail,
    update_transaction,
    delete_transaction,
)


router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["Transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction_endpoint(
    data: TransactionCreateRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> TransactionResponse:
    return create_transaction(
        db=db,
        user_id=user_id,
        data=data,
    )


@router.get(
    "",
    response_model=TransactionListResponse,
)
def list_transactions(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    type: Literal["income", "expense"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort_by: Literal[
        "transaction_at",
        "amount",
        "title",
    ] = "transaction_at",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
) -> TransactionListResponse:

    return get_transactions(
        db=db,
        user_id=user_id,
        type=type,
        page=page,
        page_size=page_size,
        category_id=category_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/daily-net-totals",
    response_model=list[DailyNetTotalResponse],
)
def get_daily_net_totals_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    type: Literal["income", "expense"] | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> list[DailyNetTotalResponse]:
    return get_daily_net_totals(
        db=db,
        user_id=user_id,
        type=type,
        category_id=category_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionDetailResponse,
)
def get_transaction_detail_endpoint(
    transaction_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    return get_transaction_detail(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
    )


@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction_endpoint(
    transaction_id: int,
    data: TransactionUpdateRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> TransactionResponse:
    return update_transaction(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
        data=data,
    )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction_endpoint(
    transaction_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> None:
    delete_transaction(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
    )