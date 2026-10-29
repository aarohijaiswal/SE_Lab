
import pytest

from bus_transit_fare import (
    process_commute_manifest,
    inspect_smartcard_turnstiles,
)


def test_invalid_manifests():
    with pytest.raises(ValueError):
        process_commute_manifest("invalid", 2.0)


def test_negative_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_inactive_route_is_skipped():
    result = process_commute_manifest(
        [{"route_active": False, "commuters": [{"zones": 2}]}], 2.0
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


@pytest.mark.parametrize(
    "route_type, expected",
    [("local", 4.5), ("shuttle", 6.0), ("express", 8.0)],
)
def test_route_types(route_type, expected):
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": route_type,
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result["total_fare"] == expected


def test_unknown_route_is_rejected():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "unknown", "commuters": []}],
        2.0,
    )
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


@pytest.mark.parametrize(
    "passenger_type, expected",
    [("regular", 4.5), ("student", 1.75), ("senior", 2.45)],
)
def test_passenger_types(passenger_type, expected):
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": passenger_type}],
        }],
        2.0,
    )
    assert result["total_fare"] == expected


def test_default_commuter_values():
    result = process_commute_manifest(
        [{"route_active": True, "commuters": [{}]}], 2.0
    )
    assert result["total_fare"] == 3.5


def test_zero_or_negative_zones_reject_rides():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "commuters": [{"zones": 0}, {"zones": -1}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_card_on_local_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "blacklisted": True}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_card_on_express_resets_fare():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 1, "type": "regular"},
                {"zones": 1, "blacklisted": True},
            ],
        }],
        2.0,
    )
    assert result["total_fare"] == 0.0


def test_priority_boarding_fee():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [{"zones": 2}],
        }],
        2.0,
    )
    assert result["total_fare"] == 6.5


def test_audit_rejected_after_more_than_four_rejections():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "commuters": [{"zones": 0} for _ in range(5)],
        }],
        2.0,
    )
    assert result["status"] == "AUDIT_REJECTED"


def test_no_turnstile_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstiles_operational():
    assert inspect_smartcard_turnstiles([[1, 4, 2, 5, 1]]) == "OPERATIONAL"


def test_turnstile_jam_after_consecutive_high_failures():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstile_failure_streak_resets():
    assert inspect_smartcard_turnstiles([[4, 2, 5]]) == "OPERATIONAL"
