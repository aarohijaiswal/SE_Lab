
import pytest

from bus_transit_fare import (
    process_commute_manifest,
    inspect_smartcard_turnstiles,
)


def test_manifests_must_be_a_list():
    with pytest.raises(ValueError):
        process_commute_manifest("invalid", 2.0)


def test_booking_fee_must_not_be_negative():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_empty_manifests():
    assert process_commute_manifest([], 2.0) == {
        "total_fare": 0.0,
        "status": "ZERO_RIDERSHIP",
    }


@pytest.mark.parametrize("route_type, expected", [
    ("express", 8.0),
    ("shuttle", 6.0),
    ("local", 4.5),
    ("unknown", 0.0),
])
def test_all_route_type_outcomes(route_type, expected):
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": route_type,
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result["total_fare"] == expected


def test_inactive_route_and_default_route():
    result = process_commute_manifest(
        [
            {"route_active": False, "commuters": [{"zones": 1}]},
            {"route_active": True, "commuters": [{}]},
        ],
        2.0,
    )
    assert result["total_fare"] == 3.5


@pytest.mark.parametrize("passenger_type, expected", [
    ("student", 1.75),
    ("senior", 2.45),
    ("regular", 4.5),
    ("unknown", 4.5),
])
def test_all_passenger_type_outcomes(passenger_type, expected):
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": passenger_type}],
        }],
        2.0,
    )
    assert result["total_fare"] == expected


@pytest.mark.parametrize("zones", [0, -1])
def test_nonpositive_zones(zones):
    result = process_commute_manifest(
        [{
            "route_active": True,
            "commuters": [{"zones": zones}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_non_express_passenger():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 1, "blacklisted": True}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_express_passenger_resets_fare():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 1},
                {"zones": 1, "blacklisted": True},
            ],
        }],
        2.0,
    )
    assert result["total_fare"] == 0.0


def test_priority_boarding_enabled_and_disabled():
    result = process_commute_manifest(
        [
            {
                "route_active": True,
                "priority_boarding": True,
                "commuters": [{"zones": 1}],
            },
            {
                "route_active": True,
                "priority_boarding": False,
                "commuters": [{"zones": 1}],
            },
        ],
        2.0,
    )
    assert result["total_fare"] == 9.0


def test_audit_rejected_when_rejections_exceed_four():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "commuters": [{"zones": 0} for _ in range(5)],
        }],
        2.0,
    )
    assert result["status"] == "AUDIT_REJECTED"


def test_completed_status_with_positive_fare():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "commuters": [{"zones": 1}],
        }],
        2.0,
    )
    assert result["status"] == "COMPLETED"


def test_turnstile_empty_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


@pytest.mark.parametrize("readings", [
    [[1, 2, 3]],
    [[4, 2, 5]],
    [[4, 4]],
])
def test_turnstile_operational_or_reset(readings):
    expected = "TURNSTILE_JAM" if readings == [[4, 4]] else "OPERATIONAL"
    assert inspect_smartcard_turnstiles(readings) == expected


def test_turnstile_jam_on_consecutive_high_failures():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstile_streak_resets_after_low_reading():
    assert inspect_smartcard_turnstiles([[4, 2, 5]]) == "OPERATIONAL"
