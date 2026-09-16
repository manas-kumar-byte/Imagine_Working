import React, { useEffect, useRef, useState } from "react";

import {
  getFacilityStatus,
  getMedicines,
  getRegionRisk,
} from "../api/client";

// Facilities colored by type.
// Regions shaded by regional_risk_score.
// This is the demo's money shot — prioritize this component's polish.
// Owner: Frontend/Product Lead

export default function MapView({
  facilities = [],
  regionRisk = {},
}) {
  /*
   * ============================================================
   * REGION LAYOUT
   *
   * The map now has FOUR regions:
   *
   *              NORTH          EAST
   *          ┌──────────┬─────────────────┐
   *          │          │                 │
   *          │          │                 │
   *          ├──────────┤                 │
   *          │   WEST   │                 │
   *          │          ├─────────────────┤
   *          │          │                 │
   *          └──────────┴─────────────────┘
   *                 SOUTH
   *
   * ============================================================
   */

  const REGION_BOUNDS = {
    reg_north: {
      minX: 30,
      maxX: 460,
      minY: 30,
      maxY: 220,
    },

    reg_east: {
      minX: 490,
      maxX: 970,
      minY: 30,
      maxY: 320,
    },

    reg_west: {
      minX: 30,
      maxX: 460,
      minY: 240,
      maxY: 390,
    },

    reg_south: {
      minX: 30,
      maxX: 970,
      minY: 410,
      maxY: 570,
    },
  };

  /*
   * ============================================================
   * HOVER STATE
   * ============================================================
   */

  const [medicines, setMedicines] = useState([]);

  const [hoveredFacility, setHoveredFacility] =
    useState(null);

  const [facilityStatuses, setFacilityStatuses] =
    useState([]);

  const [loadingStatuses, setLoadingStatuses] =
    useState(false);

  const [hoveredRegion, setHoveredRegion] =
    useState(null);

  const [regionRisks, setRegionRisks] =
    useState([]);

  const [loadingRegionRisk, setLoadingRegionRisk] =
    useState(false);

  const regionRiskCache = useRef({});
  const facilityStatusCache = useRef({});
  const facilityHoverIdRef = useRef(null);

  /*
   * ============================================================
   * HOVER TIMERS
   *
   * These stop the region card from disappearing when the
   * mouse moves from the region into the floating card.
   * ============================================================
   */

  const regionLeaveTimer = useRef(null);

  /*
   * ============================================================
   * STATUS COLORS
   * ============================================================
   */

  const STATUS_COLORS = {
    healthy: "#2e7d32",
    watch: "#f9a825",
    critical: "#ef6c00",
    stockout: "#c62828",
  };

  /*
   * ============================================================
   * LOAD MEDICINES
   * ============================================================
   */

  useEffect(() => {
    async function loadMedicines() {
      try {
        const data = await getMedicines();

        setMedicines(data);
      } catch (error) {
        console.error(
          "Failed to load medicines:",
          error
        );
      }
    }

    loadMedicines();

    return () => {
      clearTimeout(
        regionLeaveTimer.current
      );
    };
  }, []);

  /*
   * ============================================================
   * GET FACILITIES FOR REGION
   * ============================================================
   */

  const getRegionFacilities = (regionId) => {
    return facilities.filter(
      (facility) =>
        facility.region_id === regionId
    );
  };

  /*
   * ============================================================
   * FACILITY POSITIONING
   *
   * Converts the real lat/lon values into positions inside
   * the artificial SVG region.
   *
   * This means the fake map does NOT need a real map image.
   * ============================================================
   */

  const getFacilityPosition = (facility) => {
    const region =
      REGION_BOUNDS[facility.region_id];

    /*
     * Unknown region:
     * Put it somewhere safe in the middle.
     */

    if (!region) {
      return {
        x: 500,
        y: 300,
      };
    }

    const regionFacilities =
      getRegionFacilities(
        facility.region_id
      );

    /*
     * Extract coordinates for facilities
     * inside this region.
     */

    const lats =
      regionFacilities.map(
        (f) => Number(f.lat)
      );

    const lons =
      regionFacilities.map(
        (f) => Number(f.lon)
      );

    /*
     * Safety fallback.
     */

    if (
      lats.length === 0 ||
      lons.length === 0
    ) {
      return {
        x:
          (region.minX + region.maxX) / 2,

        y:
          (region.minY + region.maxY) / 2,
      };
    }

    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);

    const minLon = Math.min(...lons);
    const maxLon = Math.max(...lons);

    /*
     * Avoid division by zero.
     */

    const latRange =
      maxLat - minLat || 1;

    const lonRange =
      maxLon - minLon || 1;

    /*
     * Normalize longitude and latitude
     * into the 0 -> 1 range.
     */

    const normalizedX =
      (Number(facility.lon) - minLon) /
      lonRange;

    const normalizedY =
      (Number(facility.lat) - minLat) /
      latRange;

    /*
     * Padding keeps markers away from
     * region boundaries.
     */

    const padding = 28;

    const usableMinX =
      region.minX + padding;

    const usableMaxX =
      region.maxX - padding;

    const usableMinY =
      region.minY + padding;

    const usableMaxY =
      region.maxY - padding;

    /*
     * Longitude:
     *
     * low  -> left
     * high -> right
     */

    const x =
      usableMinX +
      normalizedX *
        (usableMaxX - usableMinX);

    /*
     * Latitude:
     *
     * high -> UP
     * low  -> DOWN
     */

    const y =
      usableMaxY -
      normalizedY *
        (usableMaxY - usableMinY);

    return {
      x,
      y,
    };
  };

  /*
   * ============================================================
   * FACILITY COLORS
   * ============================================================
   */

  const getFacilityColor = (facility) => {
    switch (facility.type) {
      case "hospital":
        return "#dc2626";

      case "clinic":
        return "#2563eb";

      case "pharmacy":
        return "#16a34a";

      case "warehouse":
        return "#9333ea";

      default:
        return "#64748b";
    }
  };

  /*
   * ============================================================
   * FACILITY SIZE
   * ============================================================
   */

  const getFacilityRadius = (facility) => {
    switch (facility.tier) {
      case "large":
        return 12;

      case "medium":
        return 10;

      case "small":
      default:
        return 8;
    }
  };

  /*
   * ============================================================
   * REGION RISK OPACITY
   *
   * regionRisk is expected to look like:
   *
   * {
   *   reg_north: 0.45,
   *   reg_east: 0.71,
   *   reg_west: 0.20,
   *   reg_south: 0.63
   * }
   * ============================================================
   */

  const getRiskOpacity = (regionId) => {
    const risk =
      Number(regionRisk?.[regionId]);

    if (Number.isNaN(risk)) {
      return 0.08;
    }

    const clampedRisk =
      Math.max(
        0,
        Math.min(1, risk)
      );

    return (
      0.08 +
      clampedRisk * 0.22
    );
  };

  /*
   * ============================================================
   * FACILITY HOVER
   * ============================================================
   */

const handleFacilityHover = async (facility) => {
  facilityHoverIdRef.current = facility.id;

  setHoveredFacility(facility);

  const cacheKey = facility.id;

  // Cached → instant
  if (facilityStatusCache.current[cacheKey]) {
    setFacilityStatuses(
      facilityStatusCache.current[cacheKey]
    );
    setLoadingStatuses(false);
    return;
  }

  setFacilityStatuses([]);
  setLoadingStatuses(true);

  try {
    const results = await Promise.allSettled(
      medicines.map((medicine) =>
        getFacilityStatus(
          facility.id,
          medicine.id
        )
      )
    );

    const statuses = results
      .filter(
        (result) =>
          result.status === "fulfilled"
      )
      .map(
        (result) =>
          result.value
      );

    // Cache it
    facilityStatusCache.current[cacheKey] =
      statuses;

    // User may have moved to another facility
    if (
      facilityHoverIdRef.current ===
      facility.id
    ) {
      setFacilityStatuses(statuses);
    }

  } catch (error) {
    console.error(
      "Failed to load facility statuses:",
      error
    );

    if (
      facilityHoverIdRef.current ===
      facility.id
    ) {
      setFacilityStatuses([]);
    }

  } finally {
    if (
      facilityHoverIdRef.current ===
      facility.id
    ) {
      setLoadingStatuses(false);
    }
  }
};
  /*
   * ============================================================
   * FACILITY LEAVE
   * ============================================================
   */

  const handleFacilityLeave = () => {
  facilityHoverIdRef.current = null;

  setHoveredFacility(null);
  setFacilityStatuses([]);
  setLoadingStatuses(false);
};
  /*
   * ============================================================
   * REGION HOVER
   * ============================================================
   */
  const regionHoverIdRef = useRef(null);
const handleRegionHover = async (regionId) => {
  setHoveredRegion(regionId);

  const cacheKey = regionId;

  // Already fetched
  if (regionRiskCache.current[cacheKey]) {
    setRegionRisks(regionRiskCache.current[cacheKey]);
    return;
  }

  setLoadingRegionRisk(true);

  try {
    const results = await Promise.allSettled(
      medicines.map((medicine) =>
        getRegionRisk(regionId, medicine.id)
      )
    );

    const risks = results
      .filter((r) => r.status === "fulfilled")
      .map((r) => r.value);

    regionRiskCache.current[cacheKey] = risks;

    setRegionRisks(risks);
  } finally {
    setLoadingRegionRisk(false);
  }
};

  /*
   * ============================================================
   * REGION LEAVE
   *
   * Do NOT immediately close the card.
   *
   * The user needs enough time to move the mouse from the
   * district into the foreignObject.
   * ============================================================
   */

  const handleRegionLeave = () => {
    clearTimeout(
      regionLeaveTimer.current
    );

    regionLeaveTimer.current =
      setTimeout(() => {
        setHoveredRegion(null);

        setRegionRisks([]);
      }, 300);
  };

  /*
   * ============================================================
   * REGION CARD ENTER
   *
   * The user successfully reached the card,
   * so cancel the pending close.
   * ============================================================
   */

  const handleRegionCardEnter = () => {
    clearTimeout(
      regionLeaveTimer.current
    );
  };

  /*
   * ============================================================
   * REGION CARD LEAVE
   * ============================================================
   */

  const handleRegionCardLeave = () => {
    clearTimeout(
      regionLeaveTimer.current
    );

    setHoveredRegion(null);

    setRegionRisks([]);
  };

  /*
   * ============================================================
   * FIND MEDICINE NAME
   * ============================================================
   */

  const getMedicineName = (medicineId) => {
    const medicine =
      medicines.find(
        (medicine) =>
          medicine.id === medicineId
      );

    return medicine
      ? medicine.name
      : medicineId;
  };

  /*
   * ============================================================
   * FIND REGION NAME
   * ============================================================
   */

  const getRegionName = (regionId) => {
    switch (regionId) {
      case "reg_north":
        return "North Region";

      case "reg_east":
        return "East Region";

      case "reg_west":
        return "West Region";

      case "reg_south":
        return "South Region";

      default:
        return regionId;
    }
  };

  /*
   * ============================================================
   * RENDER
   * ============================================================
   */

  return (
    <div className="map-view card">

      <h2 className="heading-text">
        Map View
      </h2>

      <div className="map-visualization-wrapper">

        <svg
          viewBox="0 0 1000 600"
          xmlns="http://www.w3.org/2000/svg"
          className="medical-city-map"
        >

          <defs>

            {/* =================================================
                URBAN TEXTURE
            ================================================= */}

            <pattern
              id="urban-texture"
              width={20}
              height={20}
              patternUnits="userSpaceOnUse"
            >
              <circle
                cx={2}
                cy={2}
                r={1}
                fill="#e0e0e0"
                opacity="0.3"
              />
            </pattern>

            {/* =================================================
                FACILITY GLOW
            ================================================= */}

            <filter
              id="facility-glow"
              x="-100%"
              y="-100%"
              width="300%"
              height="300%"
            >
              <feGaussianBlur
                stdDeviation="4"
                result="blur"
              />

              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* =================================================
                DISTRICT GLOW
            ================================================= */}

            <filter
              id="active-district"
              x="-10%"
              y="-10%"
              width="120%"
              height="120%"
            >
              <feGaussianBlur
                stdDeviation={5}
                result="blur"
              />

              <feComposite
                in="SourceGraphic"
                in2="blur"
                operator="over"
              />
            </filter>

          </defs>

          {/* ====================================================
              BASE BACKGROUND
          ==================================================== */}

          <rect
            width={1000}
            height={600}
            fill="#f8f9fa"
          />

          <rect
            width={1000}
            height={600}
            fill="url(#urban-texture)"
          />

          {/* ====================================================
              RIVER
          ==================================================== */}

          <path
            className="river-underlay"
            d="
              M -50 330
              C 180 280,
                300 430,
                470 360
              C 620 300,
                730 430,
                1050 350
            "
          />

          <path
            className="river-core"
            d="
              M -50 330
              C 180 280,
                300 430,
                470 360
              C 620 300,
                730 430,
                1050 350
            "
          />

          {/* ====================================================
              NORTH REGION
          ==================================================== */}

          <g
            className={`district high-quarter ${
              hoveredRegion === "reg_north"
                ? "region-hovered"
                : ""
            }`}
            onMouseEnter={() =>
              handleRegionHover(
                "reg_north"
              )
            }
            onMouseLeave={
              handleRegionLeave
            }
          >

            <path
              d="
                M 30 30
                L 480 30
                L 455 205
                C 360 220,
                  230 225,
                  120 220
                C 80 218,
                  50 220,
                  20 225
                Z
              "
            />

          </g>

          {/* ====================================================
              EAST REGION
          ==================================================== */}

          <g
            className={`district iron-docks ${
              hoveredRegion === "reg_east"
                ? "region-hovered"
                : ""
            }`}
            onMouseEnter={() =>
              handleRegionHover(
                "reg_east"
              )
            }
            onMouseLeave={
              handleRegionLeave
            }
          >

            <path
              d="
                M 480 30
                L 970 30
                L 970 330
                C 860 340,
                  760 300,
                  660 315
                C 570 330,
                  500 275,
                  455 205
                L 480 30
                Z
              "
            />

          </g>

          {/* ====================================================
              WEST REGION
          ==================================================== */}

          <g
            className={`district west-quarter ${
              hoveredRegion === "reg_west"
                ? "region-hovered"
                : ""
            }`}
            onMouseEnter={() =>
              handleRegionHover(
                "reg_west"
              )
            }
            onMouseLeave={
              handleRegionLeave
            }
          >

            <path
              d="
                M 20 225
                C 100 220,
                  250 225,
                  455 205
                C 475 250,
                  500 300,
                  530 350
                C 500 370,
                  475 385,
                  455 395
                L 30 395
                Z
              "
              fill="#e8f1f8"
            />

          </g>

          {/* ====================================================
              SOUTH REGION
          ==================================================== */}

          <g
            className={`district foundry-commons ${
              hoveredRegion === "reg_south"
                ? "region-hovered"
                : ""
            }`}
            onMouseEnter={() =>
              handleRegionHover(
                "reg_south"
              )
            }
            onMouseLeave={
              handleRegionLeave
            }
          >

            <path
              d="
                M 30 395
                L 455 395
                C 480 385,
                  500 370,
                  530 350
                C 650 330,
                  800 345,
                  970 330
                L 970 570
                L 30 570
                Z
              "
            />

          </g>

          {/* ====================================================
              REGION RISK OVERLAYS
          ==================================================== */}

          {/* NORTH */}

          <path
            className="risk-overlay north-risk"
            d="
              M 30 30
              L 480 30
              L 455 205
              C 360 220,
                230 225,
                120 220
              C 80 218,
                50 220,
                20 225
              Z
            "
            opacity={getRiskOpacity(
              "reg_north"
            )}
          />

          {/* EAST */}

          <path
            className="risk-overlay east-risk"
            d="
              M 480 30
              L 970 30
              L 970 330
              C 860 340,
                760 300,
                660 315
              C 570 330,
                500 275,
                455 205
              L 480 30
              Z
            "
            opacity={getRiskOpacity(
              "reg_east"
            )}
          />

          {/* WEST */}

          <path
            className="risk-overlay west-risk"
            d="
              M 20 225
              C 100 220,
                250 225,
                455 205
              C 475 250,
                500 300,
                530 350
              C 500 370,
                475 385,
                455 395
              L 30 395
              Z
            "
            opacity={getRiskOpacity(
              "reg_west"
            )}
          />

          {/* SOUTH */}

          <path
            className="risk-overlay south-risk"
            d="
              M 30 395
              L 455 395
              C 480 385,
                500 370,
                530 350
              C 650 330,
                800 345,
                970 330
              L 970 570
              L 30 570
              Z
            "
            opacity={getRiskOpacity(
              "reg_south"
            )}
          />

          {/* ====================================================
              BUILDINGS
          ==================================================== */}

          <g className="building-layer">

            {/* ================= NORTH ================= */}

            <g className="b-block">

              <rect
                x={60}
                y={55}
                width={55}
                height={45}
                rx={3}
              />

              <rect
                x={130}
                y={55}
                width={45}
                height={35}
                rx={3}
              />

              <rect
                x={70}
                y={115}
                width={95}
                height={40}
                rx={3}
              />

              <rect
                x={190}
                y={55}
                width={50}
                height={100}
                rx={3}
              />

              <rect
                x={260}
                y={65}
                width={65}
                height={60}
                rx={3}
              />

              <rect
                x={340}
                y={65}
                width={55}
                height={80}
                rx={3}
              />

              <rect
                x={100}
                y={175}
                width={50}
                height={30}
                rx={3}
              />

              <rect
                x={170}
                y={175}
                width={75}
                height={30}
                rx={3}
              />

              <rect
                x={280}
                y={160}
                width={100}
                height={40}
                rx={3}
              />

            </g>

            {/* ================= EAST ================= */}

            <g className="b-block">

              <rect
                x={530}
                y={55}
                width={120}
                height={25}
              />

              <rect
                x={530}
                y={90}
                width={120}
                height={25}
              />

              <rect
                x={675}
                y={55}
                width={80}
                height={30}
              />

              <rect
                x={770}
                y={55}
                width={80}
                height={30}
              />

              <rect
                x={865}
                y={55}
                width={80}
                height={40}
              />

              <rect
                x={570}
                y={145}
                width={45}
                height={90}
              />

              <rect
                x={635}
                y={145}
                width={45}
                height={90}
              />

              <rect
                x={700}
                y={145}
                width={45}
                height={90}
              />

              <rect
                x={765}
                y={140}
                width={110}
                height={50}
              />

              <rect
                x={885}
                y={140}
                width={55}
                height={90}
              />

              <path
                d="
                  M 820 220
                  L 940 220
                  L 920 280
                  L 820 280
                  Z
                "
              />

            </g>

            {/* ================= WEST ================= */}

            <g className="b-block">

              <rect
                x={55}
                y={250}
                width={70}
                height={35}
                rx={3}
              />

              <rect
                x={140}
                y={250}
                width={45}
                height={60}
                rx={3}
              />

              <rect
                x={200}
                y={245}
                width={85}
                height={45}
                rx={3}
              />

              <rect
                x={300}
                y={245}
                width={55}
                height={70}
                rx={3}
              />

              <rect
                x={375}
                y={235}
                width={55}
                height={50}
                rx={3}
              />

              <rect
                x={70}
                y={325}
                width={45}
                height={45}
                rx={3}
              />

              <rect
                x={130}
                y={330}
                width={90}
                height={35}
                rx={3}
              />

              <rect
                x={245}
                y={325}
                width={55}
                height={50}
                rx={3}
              />

              <rect
                x={325}
                y={330}
                width={100}
                height={40}
                rx={3}
              />

            </g>

            {/* ================= SOUTH ================= */}

            <g className="b-block">

              <rect
                x={60}
                y={425}
                width={30}
                height={30}
              />

              <rect
                x={100}
                y={425}
                width={30}
                height={30}
              />

              <rect
                x={140}
                y={425}
                width={30}
                height={30}
              />

              <rect
                x={60}
                y={465}
                width={30}
                height={30}
              />

              <rect
                x={100}
                y={465}
                width={30}
                height={30}
              />

              <rect
                x={140}
                y={465}
                width={30}
                height={30}
              />

              <rect
                x={195}
                y={425}
                width={85}
                height={60}
              />

              <rect
                x={300}
                y={425}
                width={100}
                height={40}
              />

              <rect
                x={70}
                y={510}
                width={100}
                height={50}
              />

              <rect
                x={195}
                y={505}
                width={60}
                height={50}
              />

              <rect
                x={275}
                y={500}
                width={130}
                height={60}
              />

              <rect
                x={480}
                y={430}
                width={80}
                height={100}
              />

              <rect
                x={580}
                y={425}
                width={110}
                height={45}
              />

              <rect
                x={715}
                y={425}
                width={55}
                height={50}
              />

              <rect
                x={795}
                y={420}
                width={80}
                height={110}
              />

              <rect
                x={590}
                y={490}
                width={170}
                height={65}
              />

              <rect
                x={890}
                y={445}
                width={55}
                height={100}
              />

            </g>

          </g>

          {/* ====================================================
              MAIN ROADS
          ==================================================== */}

          <g className="road-network">

            {/* North horizontal artery */}

            <path
              className="main-artery"
              d="
                M 30 170
                L 455 170
                L 600 315
                L 970 315
              "
            />

            {/* Central vertical artery */}

            <path
              className="main-artery"
              d="
                M 460 30
                L 460 205
                L 490 270
                L 500 395
                L 500 570
              "
            />

            {/* West vertical artery */}

            <path
              className="main-artery"
              d="
                M 250 30
                L 250 220
                L 250 395
                L 250 570
              "
            />

            {/* East vertical artery */}

            <path
              className="main-artery"
              d="
                M 700 30
                L 700 315
                L 700 570
              "
            />

            {/* South horizontal artery */}

            <path
              className="main-artery"
              d="
                M 30 470
                L 500 470
                L 700 470
                L 970 470
              "
            />

            {/* ==================================================
                SECONDARY STREETS
            ================================================== */}

            {/* North */}

            <path
              className="local-street"
              d="M 70 110 L 250 110"
            />

            <path
              className="local-street"
              d="M 170 110 L 170 170"
            />

            <path
              className="local-street"
              d="M 250 70 L 460 70"
            />

            <path
              className="local-street"
              d="M 370 70 L 370 170"
            />

            {/* East */}

            <path
              className="local-street"
              d="M 530 130 L 700 130"
            />

            <path
              className="local-street"
              d="M 650 30 L 650 130"
            />

            <path
              className="local-street"
              d="M 700 110 L 970 110"
            />

            <path
              className="local-street"
              d="M 820 110 L 820 315"
            />

            {/* West */}

            <path
              className="local-street"
              d="M 55 315 L 250 315"
            />

            <path
              className="local-street"
              d="M 150 250 L 150 395"
            />

            <path
              className="local-street"
              d="M 250 280 L 455 280"
            />

            <path
              className="local-street"
              d="M 350 220 L 350 395"
            />

            {/* South */}

            <path
              className="local-street"
              d="M 70 400 L 70 570"
            />

            <path
              className="local-street"
              d="M 180 400 L 180 570"
            />

            <path
              className="local-street"
              d="M 350 400 L 350 570"
            />

            <path
              className="local-street"
              d="M 500 400 L 500 570"
            />

            <path
              className="local-street"
              d="M 570 410 L 570 570"
            />

            <path
              className="local-street"
              d="M 700 400 L 700 570"
            />

            <path
              className="local-street"
              d="M 850 400 L 850 570"
            />

            <path
              className="local-street"
              d="M 700 525 L 970 525"
            />

          </g>

          {/* ====================================================
              BRIDGES
          ==================================================== */}

          <rect
            x={447}
            y={195}
            width={22}
            height={28}
            fill="#78909c"
            stroke="#37474f"
            strokeWidth={1}
          />

          <rect
            x={520}
            y={330}
            width={30}
            height={20}
            fill="#78909c"
            stroke="#37474f"
            strokeWidth={1}
            transform="rotate(42, 520, 330)"
          />

          {/* ====================================================
              REGION LABELS
          ==================================================== */}

          <g className="map-ui-labels">

            <text
              x={210}
              y={55}
              className="label-heading"
            >
              NORTH REGION
            </text>

            <text
              x={720}
              y={55}
              className="label-heading"
            >
              EAST REGION
            </text>

            <text
              x={205}
              y={250}
              className="label-heading"
            >
              WEST REGION
            </text>

            <text
              x={430}
              y={555}
              className="label-heading"
            >
              SOUTH REGION
            </text>

          </g>

          {/* ====================================================
              FACILITY MARKERS
          ==================================================== */}

          <g className="facility-layer">

            {facilities.map((facility) => {

              const {
                x,
                y,
              } =
                getFacilityPosition(
                  facility
                );

              const color =
                getFacilityColor(
                  facility
                );

              const radius =
                getFacilityRadius(
                  facility
                );

              const isHovered =
                hoveredFacility?.id ===
                facility.id;

              return (
                <g
                  key={facility.id}
                  className="facility-marker"

                  onMouseEnter={() =>
                    handleFacilityHover(
                      facility
                    )
                  }

                  onMouseLeave={
                    handleFacilityLeave
                  }
                >

                  {/* Hover glow */}

                  <circle
                    cx={x}
                    cy={y}
                    r={
                      isHovered
                        ? radius + 10
                        : radius + 5
                    }
                    fill={color}
                    opacity={
                      isHovered
                        ? 0.28
                        : 0.15
                    }
                    filter="url(#facility-glow)"
                    className="facility-glow"
                  />

                  {/* Main marker */}

                  <circle
                    cx={x}
                    cy={y}
                    r={
                      isHovered
                        ? radius + 2
                        : radius
                    }
                    fill={color}
                    stroke="white"
                    strokeWidth={3}
                    className="facility-dot"
                  />

                  {/* Inner dot */}

                  <circle
                    cx={x}
                    cy={y}
                    r={3}
                    fill="white"
                    pointerEvents="none"
                  />

                  {/* Facility name */}

                  <text
                    x={x + radius + 7}
                    y={y + 4}
                    className={
                      isHovered
                        ? "facility-label facility-label-active"
                        : "facility-label"
                    }
                  >
                    {facility.name}
                  </text>

                  {/* Browser tooltip */}

                  <title>
                    {facility.name}
                    {"\n"}
                    Type: {facility.type}
                    {"\n"}
                    Tier: {facility.tier}
                    {"\n"}
                    Population served:{" "}
                    {Number(
                      facility.population_served
                    ).toLocaleString()}
                  </title>

                </g>
              );
            })}

          </g>

          {/* ====================================================
              FACILITY STATUS HOVER CARD
          ==================================================== */}

          {hoveredFacility && (
            (() => {

              const {
                x,
                y,
              } =
                getFacilityPosition(
                  hoveredFacility
                );

              const cardWidth = 275;
              const cardHeight = 330;

              let cardX = x + 25;
              let cardY = y - 100;

              /*
               * Keep inside right edge.
               */

              if (
                cardX + cardWidth > 990
              ) {
                cardX =
                  x -
                  cardWidth -
                  25;
              }

              /*
               * Keep inside top edge.
               */

              if (cardY < 10) {
                cardY = 10;
              }

              /*
               * Keep inside bottom edge.
               */

              if (
                cardY + cardHeight > 590
              ) {
                cardY =
                  590 -
                  cardHeight;
              }

              return (
                <foreignObject
                  x={cardX}
                  y={cardY}
                  width={cardWidth}
                  height={cardHeight}
                  className="facility-status-foreign-object"
                  pointerEvents="none"
                >

                  <div className="facility-status-card">

                    {/* HEADER */}

                    <div className="facility-status-header">

                      <div className="facility-status-icon">

                        {hoveredFacility.type ===
                        "hospital"
                          ? "H"
                          : hoveredFacility.type ===
                            "clinic"
                          ? "C"
                          : hoveredFacility.type ===
                            "pharmacy"
                          ? "P"
                          : hoveredFacility.type ===
                            "warehouse"
                          ? "W"
                          : "F"}

                      </div>

                      <div className="facility-status-heading">

                        <div className="facility-status-title">
                          {
                            hoveredFacility.name
                          }
                        </div>

                        <div className="facility-status-subtitle">
                          {
                            hoveredFacility.type
                          }
                          {" • "}
                          {
                            hoveredFacility.tier
                          }
                        </div>

                      </div>

                    </div>

                    {/* DIVIDER */}

                    <div className="facility-status-divider" />

                    {/* MEDICINES */}

                    <div className="facility-status-list">

                      {loadingStatuses ? (

                        <div className="facility-status-loading">

                          <div className="loading-spinner" />

                          Loading medicine status...

                        </div>

                      ) : facilityStatuses.length ===
                        0 ? (

                        <div className="facility-status-loading">

                          No status data available.

                        </div>

                      ) : (

                        facilityStatuses.map(
                          (status) => {

                            const medicineName =
                              getMedicineName(
                                status.medicine_id
                              );

                            const statusColor =
                              STATUS_COLORS[
                                status.status
                              ] ||
                              "#64748b";

                            return (
                              <div
                                key={
                                  status.medicine_id
                                }
                                className="medicine-status-row"
                              >

                                <div className="medicine-info">

                                  <div className="medicine-name">
                                    {
                                      medicineName
                                    }
                                  </div>

                                </div>

                                <div
                                  className="medicine-status"
                                  style={{
                                    color:
                                      statusColor,
                                  }}
                                >

                                  <span
                                    className="status-dot"
                                    style={{
                                      backgroundColor:
                                        statusColor,
                                    }}
                                  />

                                  {
                                    status.status
                                  }

                                </div>

                              </div>
                            );
                          }
                        )

                      )}

                    </div>

                    {/* STATUS LEGEND */}

                    {!loadingStatuses &&
                      facilityStatuses.length >
                        0 && (

                        <div className="status-mini-legend">

                          <span>
                            <i
                              style={{
                                background:
                                  STATUS_COLORS.healthy,
                              }}
                            />
                            Healthy
                          </span>

                          <span>
                            <i
                              style={{
                                background:
                                  STATUS_COLORS.watch,
                              }}
                            />
                            Watch
                          </span>

                          <span>
                            <i
                              style={{
                                background:
                                  STATUS_COLORS.critical,
                              }}
                            />
                            Critical
                          </span>

                          <span>
                            <i
                              style={{
                                background:
                                  STATUS_COLORS.stockout,
                              }}
                            />
                            Stockout
                          </span>

                        </div>

                      )}

                  </div>

                </foreignObject>
              );
            })()
          )}

          {/* ====================================================
              REGION RISK HOVER CARD
          ==================================================== */}

          {hoveredRegion && (
            (() => {

              /*
               * Position the card differently for each region
               * so it doesn't cover the entire map.
               */

              let cardX = 40;
              let cardY = 65;

              if (
                hoveredRegion ===
                "reg_east"
              ) {
                cardX = 650;
                cardY = 65;
              }

              if (
                hoveredRegion ===
                "reg_west"
              ) {
                cardX = 40;
                cardY = 225;
              }

              if (
                hoveredRegion ===
                "reg_south"
              ) {
                cardX = 560;
                cardY = 245;
              }

              const cardWidth = 300;
              const cardHeight = 320;

              return (
                <foreignObject
                  x={cardX}
                  y={cardY}
                  width={cardWidth}
                  height={cardHeight}
                  className="region-risk-foreign-object"

                  /*
                   * IMPORTANT:
                   *
                   * There is intentionally NO
                   * pointerEvents="none" here.
                   *
                   * The card needs to receive mouse events
                   * so the user can move into it and scroll.
                   */

                  onMouseEnter={
                    handleRegionCardEnter
                  }

                  onMouseLeave={
                    handleRegionCardLeave
                  }
                >

                  <div className="region-risk-card">

                    {/* =================================================
                        HEADER
                    ================================================= */}

                    <div className="region-risk-header">

                      <div className="region-risk-icon">
                        R
                      </div>

                      <div className="region-risk-heading">

                        <div className="region-risk-title">
                          {getRegionName(
                            hoveredRegion
                          )}
                        </div>

                        <div className="region-risk-subtitle">
                          Regional Risk
                        </div>

                      </div>

                    </div>

                    <div className="region-risk-divider" />

                    {/* =================================================
                        MEDICINE RISK LIST
                    ================================================= */}

                    <div className="region-risk-list">

                      {loadingRegionRisk ? (

                        <div className="region-risk-loading">

                          <div className="loading-spinner" />

                          Loading regional risk...

                        </div>

                      ) : regionRisks.length ===
                        0 ? (

                        <div className="region-risk-loading">

                          No risk data available.

                        </div>

                      ) : (

                        regionRisks.map(
                          (risk) => (

                            <div
                              key={
                                risk.medicine_id
                              }
                              className="region-risk-row"
                            >

                              <div className="region-risk-medicine">

                                <div className="region-risk-medicine-name">
                                  {getMedicineName(
                                    risk.medicine_id
                                  )}
                                </div>

                                <div className="region-risk-at-risk">

                                  {
                                    risk.facilities_at_risk
                                  }

                                  {" / "}

                                  {
                                    risk.total_facilities
                                  }

                                  {" facilities at risk"}

                                </div>

                              </div>

                              <div className="region-risk-score">

                                {(
                                  Number(
                                    risk.regional_risk_score
                                  ) * 100
                                ).toFixed(0)}

                                %

                              </div>

                            </div>

                          )
                        )

                      )}

                    </div>

                    {/* =================================================
                        SUMMARY
                    ================================================= */}

                    {!loadingRegionRisk &&
                      regionRisks.length >
                        0 && (

                        <div className="region-risk-summary">

                          <div>

                            <span>
                              Medicines tracked
                            </span>

                            <strong>
                              {
                                regionRisks.length
                              }
                            </strong>

                          </div>

                          <div>

                            <span>
                              Overall trend
                            </span>

                            <strong>

                              {regionRisks.some(
                                (risk) =>
                                  risk.trend_direction ===
                                  "worsening"
                              )
                                ? "Worsening"
                                : regionRisks.some(
                                    (risk) =>
                                      risk.trend_direction ===
                                      "improving"
                                  )
                                ? "Improving"
                                : "Stable"}

                            </strong>

                          </div>

                        </div>

                      )}

                  </div>

                </foreignObject>
              );
            })()
          )}

          {/* ====================================================
              LEGEND
          ==================================================== */}

          <g
            className="map-legend"
            transform="translate(755, 505)"
          >

            <rect
              x={0}
              y={0}
              width={200}
              height={85}
              rx={8}
              fill="white"
              opacity={0.92}
              stroke="#cbd5e1"
            />

            {/* Hospital */}

            <circle
              cx={20}
              cy={18}
              r={7}
              fill="#dc2626"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={35}
              y={22}
              className="legend-text"
            >
              Hospital
            </text>

            {/* Clinic */}

            <circle
              cx={105}
              cy={18}
              r={7}
              fill="#2563eb"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={120}
              y={22}
              className="legend-text"
            >
              Clinic
            </text>

            {/* Pharmacy */}

            <circle
              cx={20}
              cy={43}
              r={7}
              fill="#16a34a"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={35}
              y={47}
              className="legend-text"
            >
              Pharmacy
            </text>

            {/* Warehouse */}

            <circle
              cx={105}
              cy={43}
              r={7}
              fill="#9333ea"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={120}
              y={47}
              className="legend-text"
            >
              Warehouse
            </text>

            {/* Facility count */}

            <text
              x={20}
              y={72}
              className="legend-text"
            >
              {facilities.length} facilities
            </text>

          </g>

        </svg>

      </div>

    </div>
  );
}

