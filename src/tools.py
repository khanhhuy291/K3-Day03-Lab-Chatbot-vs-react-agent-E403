"""Tools cho Trợ Lý Tìm và Đặt Lịch Xem Nhà Trọ / Căn Hộ.

Các tool dùng dữ liệu demo tại ``config/rental_listings.json``. Đây không phải
tin đăng trực tiếp; agent phải nói rõ người dùng cần xác minh phòng còn trống
và điều khoản với chủ nhà trước khi đặt cọc.
"""

from __future__ import annotations

import csv
import json
from datetime import date as Date
from datetime import datetime
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BOOKINGS_PATH = Path(__file__).resolve().parents[1] / "config" / "viewing_bookings.json"
DATA_FILES = [
    ("hn.csv", "Hà Nội"),
    ("hcm.csv", "Hồ Chí Minh"),
    ("dn.csv", "Đà Nẵng"),
]


def _load_listings() -> list[dict[str, Any]]:
    """Đọc dữ liệu phòng trọ từ các file CSV trong thư mục data/."""
    listings: list[dict[str, Any]] = []

    for filename, city_name in DATA_FILES:
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            continue

        with csv_path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = (row.get("title") or "").strip()
                address = (row.get("address") or "").strip()
                if not title or not address:
                    continue

                try:
                    price = float((row.get("price") or "0").replace(",", "."))
                except (TypeError, ValueError):
                    continue

                acreage = (row.get("acreage") or "").strip()
                if price <= 0 or not acreage:
                    continue

                listings.append(
                    {
                        "title": title,
                        "price": price,
                        "published": row.get("published") or "",
                        "acreage": acreage,
                        "address": address,
                        "city": city_name,
                    }
                )

    if not listings:
        raise RuntimeError("Không thể đọc dữ liệu phòng trọ từ thư mục data/.")

    return listings


def _normalise(text: str) -> str:
    return " ".join(text.casefold().strip().split())


def _listing_id(index: int) -> str:
    """Sinh ID ổn định từ thứ tự bản ghi, không làm thay đổi schema dataset."""
    return f"APT-{index:03d}"


def _public_listing(listing: dict[str, Any], index: int) -> dict[str, Any]:
    """Bổ sung ID chỉ ở kết quả tool, còn dataset vẫn giữ đúng 5 cột nguồn."""
    return {"id": _listing_id(index), **listing}


def _load_bookings() -> list[dict[str, Any]]:
    """Đọc lịch hẹn đã lưu; file rỗng/chưa tồn tại được hiểu là chưa có lịch."""
    if not BOOKINGS_PATH.exists():
        return []
    try:
        with BOOKINGS_PATH.open(encoding="utf-8") as file:
            bookings = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Không thể đọc dữ liệu lịch hẹn: {error}") from error
    if not isinstance(bookings, list):
        raise RuntimeError("Dữ liệu lịch hẹn phải là một danh sách JSON.")
    return bookings


def _save_bookings(bookings: list[dict[str, Any]]) -> None:
    """Lưu toàn bộ lịch hẹn dưới dạng JSON dễ kiểm tra trong bài Lab."""
    BOOKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BOOKINGS_PATH.open("w", encoding="utf-8") as file:
        json.dump(bookings, file, ensure_ascii=False, indent=2)
        file.write("\n")


def search_apartments(
    location: str,
    max_price: int,
    amenities: list[str] | None = None,
) -> str:
    """Tìm phòng/căn hộ đang trống theo khu vực, ngân sách và tiện ích.

    Args:
        location: Một trong các khu vực Cầu Giấy, Thủ Đức, Quận 1,
            Bình Thạnh hoặc Gò Vấp.
        max_price: Ngân sách tối đa theo VNĐ/tháng, phải lớn hơn 0.
        amenities: Danh sách tiện ích cần có, ví dụ ``["máy lạnh", "ban công"]``.
            Vì dataset nguồn chỉ có 5 cột, tool dò tiện ích trong trường ``title``.

    Returns:
        JSON gồm kết quả phù hợp. Danh sách rỗng là một kết quả hợp lệ, không
        được suy diễn rằng có căn phòng khác đang còn trống.
    """
    if not isinstance(location, str) or not location.strip():
        return json.dumps({"error": "location là bắt buộc."}, ensure_ascii=False)
    if not isinstance(max_price, int) or isinstance(max_price, bool) or max_price <= 0:
        return json.dumps(
            {"error": "max_price phải là số nguyên dương tính theo VNĐ/tháng."},
            ensure_ascii=False,
        )
    if amenities is not None and (
        not isinstance(amenities, list) or not all(isinstance(item, str) and item.strip() for item in amenities)
    ):
        return json.dumps({"error": "amenities phải là danh sách chuỗi không rỗng."}, ensure_ascii=False)

    query_location = _normalise(location)
    requested_amenities = {_normalise(item) for item in amenities or []}
    listings = _load_listings()
    matched = []
    for index, listing in enumerate(listings, start=1):
        searchable_text = _normalise(f"{listing['title']} {listing['address']} {listing.get('city', '')}")
        price_vnd = listing["price"] * 1_000_000
        if (
            query_location in searchable_text
            and price_vnd <= max_price
            and all(item in searchable_text for item in requested_amenities)
        ):
            matched.append(_public_listing(listing, index))

    top_matches = matched[:10]

    return json.dumps(
        {
            "location": location,
            "max_price_million_vnd": max_price / 1_000_000,
            "required_amenities": amenities or [],
            "count": len(matched),
            "shown": len(top_matches),
            "listings": top_matches,
            "notice": "Dữ liệu lấy từ các file CSV trong thư mục data/; hãy xác minh tình trạng thực tế trước khi đặt cọc.",
        },
        ensure_ascii=False,
        indent=2,
    )


def book_viewing(
    apartment_id: str,
    date: str | None = None,
    appointment_time: str | None = None,
    user_name: str | None = None,
) -> str:
    """Đặt lịch xem một căn đang trống.

    Args:
        apartment_id: ID do ``search_apartments`` trả về.
        date: Ngày xem ở định dạng ``YYYY-MM-DD``.
        appointment_time: Giờ xem ở định dạng 24 giờ ``HH:MM``.
        user_name: Tên người đặt lịch.

    Returns:
        JSON xác nhận hoặc lỗi nghiệp vụ. Khi thành công, tool lưu lịch vào
        ``config/viewing_bookings.json``; vẫn cần chủ nhà xác nhận ở thực tế.
    """
    missing = [
        field
        for field, value in {
            "apartment_id": apartment_id,
            "date": date,
            "appointment_time": appointment_time,
            "user_name": user_name,
        }.items()
        if not isinstance(value, str) or not value.strip()
    ]
    if missing:
        return json.dumps(
            {"error": "Thiếu thông tin bắt buộc.", "missing_fields": missing},
            ensure_ascii=False,
        )

    try:
        viewing_date = datetime.strptime(date, "%Y-%m-%d").date()
        datetime.strptime(appointment_time, "%H:%M")
    except ValueError:
        return json.dumps(
            {"error": "Ngày/giờ không hợp lệ. Dùng YYYY-MM-DD và HH:MM (24 giờ)."},
            ensure_ascii=False,
        )
    if viewing_date < Date.today():
        return json.dumps({"error": "Ngày xem phải là hôm nay hoặc trong tương lai."}, ensure_ascii=False)

    listing_match = next(
        (
            (index, item)
            for index, item in enumerate(_load_listings(), start=1)
            if _listing_id(index).casefold() == apartment_id.strip().casefold()
        ),
        None,
    )
    if listing_match is None:
        return json.dumps({"error": f"Không tìm thấy căn hộ có ID '{apartment_id}'."}, ensure_ascii=False)
    index, listing = listing_match
    listing_id = _listing_id(index)

    bookings = _load_bookings()
    is_duplicate = any(
        booking.get("apartment_id") == listing_id
        and booking.get("date") == viewing_date.isoformat()
        and booking.get("appointment_time") == appointment_time
        for booking in bookings
    )
    if is_duplicate:
        return json.dumps(
            {"error": f"Căn hộ {listing_id} đã có lịch xem vào khung giờ này."},
            ensure_ascii=False,
        )

    booking_code = f"VIEW-{listing_id}-{viewing_date.strftime('%Y%m%d')}-{appointment_time.replace(':', '')}"
    booking = {
        "booking_code": booking_code,
        "apartment_id": listing_id,
        "title": listing["title"],
        "address": listing["address"],
        "price_million_vnd_per_month": listing["price"],
        "date": viewing_date.isoformat(),
        "appointment_time": appointment_time,
        "user_name": user_name.strip(),
        "status": "booking_confirmed",
    }
    bookings.append(booking)
    _save_bookings(bookings)

    return json.dumps(
        {
            "status": "booking_confirmed",
            "booking_code": booking_code,
            "apartment": {"id": listing_id, "title": listing["title"], "address": listing["address"]},
            "appointment": {"date": viewing_date.isoformat(), "time": appointment_time, "guest_name": user_name.strip()},
            "notice": "Lịch hẹn đã được lưu cục bộ; chủ nhà vẫn cần xác nhận ở thực tế.",
        },
        ensure_ascii=False,
        indent=2,
    )


AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "book_viewing": book_viewing,
}
