import React from 'react';

import {getFacilities} from "../api/client";



// Facilities colored by status; regions shaded by regional_risk_score.
// This is the demo's money shot — prioritize this component's polish.
// Owner: Frontend/Product Lead

export default function MapView({ facilities = [], regionRisk = {} }) {

  /*
   * ============================================================
   * REGION LAYOUT
   * ============================================================
   *
   * These are the visual regions of our fictional city.
   *
   * region_id determines WHICH part of the SVG a facility belongs
   * to. Latitude/longitude then determines WHERE inside that region
   * the facility appears.
   *
   * This is intentional because the SVG is not a real geographic
   * map.
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
   * FACILITY POSITIONING
   * ============================================================
   *
   * We calculate the geographic range INSIDE each region.
   *
   * Example:
   *
   * reg_north facilities have their own lat/lon range.
   * That range gets mapped into the North part of the SVG.
   *
   * This means:
   *
   *     region_id -> district
   *     lat/lon   -> position inside district
   */

  const getRegionFacilities = (regionId) => {
    return facilities.filter(
      (facility) => facility.region_id === regionId
    );
  };


  const getFacilityPosition = (facility) => {

    const region = REGION_BOUNDS[facility.region_id];

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


    const regionFacilities = getRegionFacilities(
      facility.region_id
    );


    /*
     * Extract latitude/longitude values for this region.
     */
    const lats = regionFacilities.map(
      (f) => Number(f.lat)
    );

    const lons = regionFacilities.map(
      (f) => Number(f.lon)
    );


    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);

    const minLon = Math.min(...lons);
    const maxLon = Math.max(...lons);


    /*
     * Avoid division by zero if a region ever contains
     * facilities with identical coordinates.
     */
    const latRange =
      maxLat - minLat || 1;

    const lonRange =
      maxLon - minLon || 1;


    /*
     * Normalize geographic coordinates to 0 -> 1.
     */
    const normalizedX =
      (Number(facility.lon) - minLon) / lonRange;

    const normalizedY =
      (Number(facility.lat) - minLat) / latRange;


    /*
     * Add padding so markers don't sit directly on
     * district boundaries.
     */
    const padding = 30;

    const usableMinX = region.minX + padding;
    const usableMaxX = region.maxX - padding;

    const usableMinY = region.minY + padding;
    const usableMaxY = region.maxY - padding;


    /*
     * Longitude:
     *
     * low longitude  -> left
     * high longitude -> right
     */
    const x =
      usableMinX +
      normalizedX *
        (usableMaxX - usableMinX);


    /*
     * Latitude:
     *
     * SVG Y increases downward.
     *
     * Therefore:
     *
     * high latitude -> UP
     * low latitude  -> DOWN
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
   *
   * Large hospitals get slightly larger markers.
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
   *
   * If your regionRisk object contains values such as:
   *
   * {
   *   reg_north: 0.2,
   *   reg_south: 0.8,
   *   reg_east: 0.5
   * }
   *
   * we can visually tint the region.
   *
   * If the value isn't available, use a neutral opacity.
   */

  const getRiskOpacity = (regionId) => {

    const risk = Number(regionRisk?.[regionId]);

    if (Number.isNaN(risk)) {
      return 0.08;
    }

    /*
     * Clamp between 0 and 1.
     */
    const clampedRisk =
      Math.max(0, Math.min(1, risk));

    return 0.08 + clampedRisk * 0.22;
  };


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
                L 970 420
                C 850 430,
                  750 290,
                  620 310
                C 510 325,
                  450 220,
                  420 220
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
                  420 220
                C 450 240,
                  510 325,
                  620 310
                C 750 290,
                  850 430,
                  970 420
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
              L 970 420
              C 850 430,
                750 290,
                620 310
              C 510 325,
                450 220,
                420 220
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
                420 220
              C 450 240,
                510 325,
                620 310
              C 750 290,
                850 430,
                970 420
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
              } = getFacilityPosition(facility);

              const color =
                getFacilityColor(facility);

              const radius =
                getFacilityRadius(facility);


              return (
                <g
                  key={facility.id}
                  className="facility-marker"
                >

                  {/* Glow */}

                  <circle
                    cx={x}
                    cy={y}
                    r={radius + 5}
                    fill={color}
                    opacity={0.15}
                    filter="url(#facility-glow)"
                  />


                  {/* Main marker */}

                  <circle
                    cx={x}
                    cy={y}
                    r={radius}
                    fill={color}
                    stroke="white"
                    strokeWidth={3}
                  />


                  {/* Inner dot */}

                  <circle
                    cx={x}
                    cy={y}
                    r={3}
                    fill="white"
                  />


                  {/* Facility label */}

                  <text
                    x={x + radius + 7}
                    y={y + 4}
                    className="facility-label"
                  >
                    {facility.name}
                  </text>


                  {/* Tooltip-ish information */}

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

