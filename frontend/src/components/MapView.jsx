import React, { useEffect, useState } from "react";

import {
  getFacilityStatus,
  getMedicines,
} from "../api/client";

// Facilities colored by status; regions shaded by regional_risk_score.
// This is the demo's money shot — prioritize this component's polish.
// Owner: Frontend/Product Lead

export default function MapView({
  facilities = [],
  regionRisk = {},
}) {
  /*
   * ============================================================
   * REGION LAYOUT
   * ============================================================
   */

  const REGION_BOUNDS = {
    reg_north: {
      minX: 30,
      maxX: 420,
      minY: 40,
      maxY: 220,
    },

    reg_east: {
      minX: 520,
      maxX: 950,
      minY: 40,
      maxY: 280,
    },

    reg_south: {
      minX: 40,
      maxX: 940,
      minY: 340,
      maxY: 550,
    },
  };


  /*
   * ============================================================
   * MEDICINE / FACILITY HOVER STATE
   * ============================================================
   */

  const [medicines, setMedicines] = useState([]);

  const [hoveredFacility, setHoveredFacility] =
    useState(null);

  const [facilityStatuses, setFacilityStatuses] =
    useState([]);

  const [loadingStatuses, setLoadingStatuses] =
    useState(false);


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
   *
   * We only need to fetch the medicine list once.
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
  }, []);


  /*
   * ============================================================
   * FACILITY POSITIONING
   * ============================================================
   */

  const getRegionFacilities = (regionId) => {
    return facilities.filter(
      (facility) =>
        facility.region_id === regionId
    );
  };


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
     * Extract latitude/longitude values
     * for this region.
     */

    const lats =
      regionFacilities.map(
        (f) => Number(f.lat)
      );

    const lons =
      regionFacilities.map(
        (f) => Number(f.lon)
      );


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
     * Normalize geographic coordinates
     * to 0 -> 1.
     */

    const normalizedX =
      (Number(facility.lon) - minLon) /
      lonRange;

    const normalizedY =
      (Number(facility.lat) - minLat) /
      latRange;


    /*
     * Padding keeps markers away from
     * district boundaries.
     */

    const padding = 30;

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
     * low  -> left
     * high -> right
     */

    const x =
      usableMinX +
      normalizedX *
        (usableMaxX - usableMinX);


    /*
     * Latitude:
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
   * REGION RISK
   * ============================================================
   */

  const getRiskOpacity = (regionId) => {
    const risk =
      Number(regionRisk?.[regionId]);

    if (Number.isNaN(risk)) {
      return 0.08;
    }

    /*
     * Clamp between 0 and 1.
     */

    const clampedRisk =
      Math.max(0, Math.min(1, risk));

    return (
      0.08 +
      clampedRisk * 0.22
    );
  };


  /*
   * ============================================================
   * FACILITY HOVER
   * ============================================================
   *
   * Your API requires:
   *
   * getFacilityStatus(
   *     facilityId,
   *     medicineId
   * )
   *
   * Therefore we request the status of every medicine
   * when the user hovers over a facility.
   */

  const handleFacilityHover = async (facility) => {
    setHoveredFacility(facility);

    setFacilityStatuses([]);

    setLoadingStatuses(true);


    try {
      const statuses =
        await Promise.all(
          medicines.map((medicine) =>
            getFacilityStatus(
              facility.id,
              medicine.id
            )
          )
        );

      /*
       * Only display the result if the user is
       * still hovering the same facility.
       */

      setFacilityStatuses(statuses);

    } catch (error) {
      console.error(
        "Failed to load facility statuses:",
        error
      );

      setFacilityStatuses([]);

    } finally {
      setLoadingStatuses(false);
    }
  };


  /*
   * ============================================================
   * FACILITY LEAVE
   * ============================================================
   */

  const handleFacilityLeave = () => {
    setHoveredFacility(null);
    setFacilityStatuses([]);
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
              M -50 250
              C 300 200,
                450 350,
                600 300
              C 750 250,
                800 450,
                1050 400
            "
          />

          <path
            className="river-core"
            d="
              M -50 250
              C 300 200,
                450 350,
                600 300
              C 750 250,
                800 450,
                1050 400
            "
          />


          {/* ====================================================
              DISTRICTS
          ==================================================== */}

          <g className="district high-quarter">

            <path
              d="
                M 30 30
                L 500 30
                L 420 220
                C 300 210,
                  150 230,
                  20 240
                Z
              "
            />

          </g>


          <g className="district iron-docks">
  <path
    d="
      M 500 30
      L 970 30
      L 970 320
      C 850 330,
        750 250,
        620 280
      C 510 295,
        450 200,
        420 190
      Z
    "
  />
</g>


          <g className="district foundry-commons">
  <path
    d="
      M 20 240
      C 150 230,
        300 210,
        420 190
      C 450 200,
        510 295,
        620 280
      C 750 250,
        850 330,
        970 320
      L 970 570
      L 30 570
      Z
    "
  />
</g>


          {/* ====================================================
              REGION RISK OVERLAYS
          ==================================================== */}

          <path
            className="risk-overlay north-risk"
            d="
              M 30 30
              L 500 30
              L 420 220
              C 300 210,
                150 230,
                20 240
              Z
            "
            opacity={getRiskOpacity("reg_north")}
          />


          <path
            className="risk-overlay east-risk"
            d="
  M 500 30
  L 970 30
  L 970 320
  C 850 330,
    750 250,
    620 280
  C 510 295,
    450 200,
    420 190
  Z
"
            opacity={getRiskOpacity("reg_east")}
          />


          <path
            className="risk-overlay south-risk"
            d="
  M 20 240
  C 150 230,
    300 210,
    420 190
  C 450 200,
    510 295,
    620 280
  C 750 250,
    850 330,
    970 320
  L 970 570
  L 30 570
  Z
"
            opacity={getRiskOpacity("reg_south")}
          />


          {/* ====================================================
              BUILDINGS
          ==================================================== */}

          <g className="building-layer">

            {/* ================= NORTH ================= */}

            <g className="b-block">

              <rect
                x={80}
                y={60}
                width={40}
                height={50}
                rx={3}
              />

              <rect
                x={130}
                y={60}
                width={35}
                height={35}
                rx={3}
              />

              <rect
                x={80}
                y={120}
                width={85}
                height={40}
                rx={3}
              />

              <rect
                x={180}
                y={60}
                width={50}
                height={100}
                rx={3}
              />

              <rect
                x={250}
                y={70}
                width={60}
                height={60}
                rx={3}
              />

              <rect
                x={320}
                y={70}
                width={40}
                height={80}
                rx={3}
              />

              <rect
                x={100}
                y={180}
                width={45}
                height={30}
                rx={3}
              />

              <rect
                x={160}
                y={180}
                width={70}
                height={30}
                rx={3}
              />

            </g>


            {/* ================= EAST ================= */}

            <g className="b-block">

              <rect
                x={540}
                y={60}
                width={120}
                height={25}
              />

              <rect
                x={540}
                y={95}
                width={120}
                height={25}
              />

              <rect
                x={680}
                y={60}
                width={80}
                height={30}
              />

              <rect
                x={770}
                y={60}
                width={80}
                height={30}
              />

              <rect
                x={860}
                y={60}
                width={90}
                height={40}
              />

              <rect
                x={620}
                y={150}
                width={45}
                height={80}
              />

              <rect
                x={680}
                y={150}
                width={45}
                height={80}
              />

              <rect
                x={740}
                y={150}
                width={45}
                height={80}
              />

              <rect
                x={820}
                y={140}
                width={110}
                height={50}
              />

              <path
                d="
                  M 860 210
                  L 940 210
                  L 920 260
                  L 860 260
                  Z
                "
              />

            </g>


            {/* ================= SOUTH ================= */}

            <g className="b-block">

              <rect
                x={60}
                y={280}
                width={25}
                height={25}
              />

              <rect
                x={90}
                y={280}
                width={25}
                height={25}
              />

              <rect
                x={120}
                y={280}
                width={25}
                height={25}
              />

              <rect
                x={60}
                y={315}
                width={25}
                height={25}
              />

              <rect
                x={90}
                y={315}
                width={25}
                height={25}
              />

              <rect
                x={120}
                y={315}
                width={25}
                height={25}
              />

              <rect
                x={180}
                y={280}
                width={80}
                height={60}
              />

              <rect
                x={270}
                y={280}
                width={90}
                height={40}
              />

              <rect
                x={70}
                y={370}
                width={110}
                height={70}
              />

              <rect
                x={195}
                y={370}
                width={45}
                height={45}
              />

              <rect
                x={250}
                y={370}
                width={120}
                height={50}
              />

              <rect
                x={80}
                y={460}
                width={50}
                height={90}
              />

              <rect
                x={140}
                y={460}
                width={70}
                height={40}
              />

              <rect
                x={220}
                y={460}
                width={150}
                height={90}
              />

              <rect
                x={480}
                y={420}
                width={80}
                height={110}
              />

              <rect
                x={580}
                y={420}
                width={110}
                height={50}
              />

              <rect
                x={710}
                y={420}
                width={50}
                height={50}
              />

              <rect
                x={770}
                y={420}
                width={80}
                height={120}
              />

              <rect
                x={580}
                y={480}
                width={170}
                height={60}
              />

            </g>

          </g>


          {/* ====================================================
              MAIN ROADS
          ==================================================== */}

          <g className="road-network">

            <path
              className="main-artery"
              d="
                M 30 170
                L 430 170
                L 590 315
                L 970 315
              "
            />

            <path
              className="main-artery"
              d="
                M 434 30
                L 434 170
                L 452 230
                L 460 410
                L 460 570
              "
            />

            <path
              className="main-artery"
              d="
                M 245 30
                L 245 270
                L 70 270
                L 70 570
              "
            />

            <path
              className="main-artery"
              d="
                M 700 30
                L 700 315
                L 700 570
              "
            />


            {/* Secondary streets */}

            <path
              className="local-street"
              d="M 80 115 L 245 115"
            />

            <path
              className="local-street"
              d="M 170 115 L 170 170"
            />

            <path
              className="local-street"
              d="M 245 65 L 434 65"
            />

            <path
              className="local-street"
              d="M 370 65 L 370 170"
            />

            <path
              className="local-street"
              d="M 540 135 L 700 135"
            />

            <path
              className="local-street"
              d="M 670 30 L 670 135"
            />

            <path
              className="local-street"
              d="M 700 115 L 970 115"
            />

            <path
              className="local-street"
              d="M 810 115 L 810 315"
            />

            <path
              className="local-street"
              d="M 70 355 L 460 355"
            />

            <path
              className="local-street"
              d="M 195 270 L 195 460"
            />

            <path
              className="local-street"
              d="M 70 450 L 220 450"
            />

            <path
              className="local-street"
              d="M 380 355 L 380 570"
            />

            <path
              className="local-street"
              d="M 460 410 L 700 410"
            />

            <path
              className="local-street"
              d="M 570 410 L 570 570"
            />

            <path
              className="local-street"
              d="M 700 475 L 970 475"
            />

          </g>


          {/* ====================================================
              BRIDGES
          ==================================================== */}

          <rect
            x={424}
            y={180}
            width={20}
            height={25}
            fill="#78909c"
            stroke="#37474f"
            strokeWidth={1}
          />

          <rect
            x={520}
            y={245}
            width={28}
            height={20}
            fill="#78909c"
            stroke="#37474f"
            strokeWidth={1}
            transform="rotate(42, 520, 245)"
          />


          {/* ====================================================
              REGION LABELS
          ==================================================== */}

          <g className="map-ui-labels">

            <text
              x={230}
              y={50}
              className="label-heading"
            >
              NORTH REGION
            </text>

            <text
              x={720}
              y={50}
              className="label-heading"
            >
              EAST REGION
            </text>

            <text
              x={230}
              y={585}
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
              } = getFacilityPosition(
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

                  {/* ------------------------------------------
                      Hover glow
                  ------------------------------------------- */}

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


                  {/* ------------------------------------------
                      Main marker
                  ------------------------------------------- */}

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


                  {/* ------------------------------------------
                      Inner dot
                  ------------------------------------------- */}

                  <circle
                    cx={x}
                    cy={y}
                    r={3}
                    fill="white"
                    pointerEvents="none"
                  />


                  {/* ------------------------------------------
                      Facility name
                  ------------------------------------------- */}

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


                  {/* ------------------------------------------
                      Browser tooltip
                  ------------------------------------------- */}

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
              MEDICINE STATUS HOVER CARD
          ==================================================== */}

          {hoveredFacility && (

            (() => {

              const {
                x,
                y,
              } = getFacilityPosition(
                hoveredFacility
              );


              /*
               * Card dimensions in SVG coordinates.
               */

              const cardWidth = 275;
              const cardHeight = 330;


              /*
               * Default position:
               * right of facility.
               */

              let cardX = x + 25;
              let cardY = y - 100;


              /*
               * If card would go outside right edge,
               * move it to the left of the facility.
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
               * Keep card inside top edge.
               */

              if (cardY < 10) {
                cardY = 10;
              }


              /*
               * Keep card inside bottom edge.
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

                    {/* ========================================
                        CARD HEADER
                    ========================================= */}

                    <div className="facility-status-header">

                      <div className="facility-status-icon">

                        {hoveredFacility.type ===
                        "hospital"
                          ? "H"
                          : hoveredFacility.type ===
                            "clinic"
                          ? "C"
                          : "P"}

                      </div>


                      <div className="facility-status-heading">

                        <div className="facility-status-title">

                          {
                            hoveredFacility.name
                          }

                        </div>

                        <div className="facility-status-subtitle">

                          {hoveredFacility.type}
                          {" • "}
                          {hoveredFacility.tier}

                        </div>

                      </div>

                    </div>


                    {/* ========================================
                        DIVIDER
                    ========================================= */}

                    <div className="facility-status-divider" />


                    {/* ========================================
                        MEDICINES
                    ========================================= */}

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


                    {/* ========================================
                        STATUS LEGEND
                    ========================================= */}

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
              LEGEND
          ==================================================== */}

          <g
            className="map-legend"
            transform="translate(760, 520)"
          >

            <rect
              x={0}
              y={0}
              width={190}
              height={65}
              rx={8}
              fill="white"
              opacity={0.92}
              stroke="#cbd5e1"
            />


            <circle
              cx={20}
              cy={20}
              r={7}
              fill="#dc2626"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={35}
              y={24}
              className="legend-text"
            >
              Hospital
            </text>


            <circle
              cx={100}
              cy={20}
              r={7}
              fill="#2563eb"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={115}
              y={24}
              className="legend-text"
            >
              Clinic
            </text>


            <circle
              cx={20}
              cy={45}
              r={7}
              fill="#16a34a"
              stroke="white"
              strokeWidth={2}
            />

            <text
              x={35}
              y={49}
              className="legend-text"
            >
              Pharmacy
            </text>


            <text
              x={115}
              y={49}
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