"""Unit tests for the Explicit Source-to-Table Mapping Layer (Sprint 1).

Verifies:
✓ Every required source has an explicit mapping.
✓ Every mapping points to a valid destination database table.
✓ No unexpected duplicate mappings exist.
✓ Required columns are validated and schema mismatches rejected.
✓ Unmapped columns trigger warning logs.
✓ SRC-12 is treated strictly as company enrichment without creating a duplicate table.
✓ Deterministic business key matching priority (ISIN -> NSE -> BSE -> Ticker -> Name).
✓ Source Priority: Primary values are not overwritten by enrichment.
✓ Source manifest is generated (output/source_manifest.csv).
✓ Source-to-table mapping report is generated (output/source_table_mapping.csv).
✓ Missing required sources block the pipeline.
"""
from pathlib import Path
import pandas as pd
import pytest

from src.etl.config import PROJECT_ROOT, TABLE_NAMES
from src.etl.source_mapping import (
    CompanyEnrichmentEngine,
    ManifestGenerator,
    PipelineBlockedException,
    ResolvedSource,
    SourceDefinition,
    SourceMappingRegistry,
    SourceResolver,
    SourceValidator,
)


@pytest.fixture
def config_path():
    """Path to production source mapping YAML configuration."""
    return PROJECT_ROOT / "config" / "source_mapping.yaml"


@pytest.fixture
def registry(config_path):
    """Instantiated SourceMappingRegistry."""
    return SourceMappingRegistry(config_path)


@pytest.fixture
def resolver(registry):
    """Instantiated SourceResolver searching data directories."""
    return SourceResolver(registry)


def test_source_mapping_config_exists(config_path):
    """Verify source_mapping.yaml exists and is accessible."""
    assert config_path.exists(), f"Configuration missing at {config_path}"


def test_all_12_expected_sources_configured(registry):
    """Verify registry loads exactly 12 required sources (SRC-01 to SRC-12)."""
    assert len(registry.sources) == 12
    for i in range(1, 13):
        src_id = f"SRC-{i:02d}"
        assert src_id in registry.sources, f"Source {src_id} missing from configuration"
        defn = registry.sources[src_id]
        assert defn.required is True, f"{src_id} should be required"


def test_every_mapping_points_to_valid_table(registry):
    """Verify each source maps to an approved domain table in schema."""
    valid_tables = set(TABLE_NAMES) | {"market_cap"}
    for src_id, defn in registry.sources.items():
        assert defn.destination_table in valid_tables, (
            f"{src_id} maps to invalid table: {defn.destination_table}"
        )


def test_no_unexpected_duplicate_table_mappings(registry):
    """Verify only 'companies' table receives multiple sources (SRC-01 primary & SRC-12 enrichment)."""
    dest_counts = {}
    for src_id, defn in registry.sources.items():
        dest_counts.setdefault(defn.destination_table, []).append(src_id)

    for tbl, src_ids in dest_counts.items():
        if tbl == "companies":
            assert set(src_ids) == {"SRC-01", "SRC-12"}, (
                f"Companies table expected SRC-01 and SRC-12, got {src_ids}"
            )
        else:
            assert len(src_ids) == 1, (
                f"Table '{tbl}' unexpectedly mapped to multiple sources: {src_ids}"
            )


def test_source_resolution_all_mapped(resolver):
    """Verify resolver successfully discovers and resolves all 12 source files."""
    resolved = resolver.resolve_all_sources()
    assert len(resolved) == 12

    for src_id, res in resolved.items():
        assert res.mapping_status == "MAPPED", (
            f"Source {src_id} failed resolution: {res.mapping_notes}"
        )
        assert res.source_path.exists(), f"Resolved path does not exist: {res.source_path}"
        assert res.rows_discovered > 0, f"Source {src_id} has 0 discovered rows"


def test_pre_etl_validation_passes(resolver):
    """Verify pre-ETL validator accepts complete valid source catalog."""
    resolved = resolver.resolve_all_sources()
    validator = SourceValidator(resolved)
    summary = validator.validate_pre_etl()

    assert summary["expected_sources"] == 12
    assert summary["mapped_sources"] == 12
    assert summary["missing_required_sources"] == 0
    assert summary["schema_mismatches"] == 0


def test_missing_required_source_blocks_pipeline(registry, tmp_path):
    """Verify pipeline raises PipelineBlockedException if a required source is missing."""
    empty_resolver = SourceResolver(registry, search_dirs=[tmp_path])
    resolved = empty_resolver.resolve_all_sources()
    validator = SourceValidator(resolved)

    with pytest.raises(PipelineBlockedException) as exc_info:
        validator.validate_pre_etl()
    assert "PIPELINE STATUS = BLOCKED" in str(exc_info.value)


def test_required_column_validation_and_unmapped_warning(resolver):
    """Verify required column presence check and unmapped column warning detection."""
    resolved = resolver.resolve_all_sources()
    validator = SourceValidator(resolved)

    # Valid P&L test dataframe
    df_valid = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2024-03"],
        "sales": [240893.0],
        "net_profit": [46099.0],
        "operating_profit": [48534.0],
        "some_extra_column": ["unused_info"],
    })

    mapped_df, unmapped = validator.validate_source_dataframe("SRC-02", df_valid)
    assert "some_extra_column" in unmapped

    # Missing required column ('sales')
    df_invalid = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2024-03"],
        "net_profit": [46099.0],
    })

    with pytest.raises(ValueError) as exc_info:
        validator.validate_source_dataframe("SRC-02", df_invalid)
    assert "missing required column" in str(exc_info.value).lower()


def test_src12_company_enrichment_logic():
    """Verify SRC-12 merges into companies table without overwriting primary values."""
    # Base companies table with primary values
    df_companies = pd.DataFrame([
        {
            "id": "TCS",
            "company_name": "Tata Consultancy Services Ltd",
            "website": "https://www.tcs.com",
            "about_company": "Primary about text",
            "bse_profile": "https://www.bseindia.com/stock-share-price/tcs/532540",
            "nse_profile": None,
        },
        {
            "id": "INFY",
            "company_name": "Infosys Ltd",
            "website": None,
            "about_company": "TCS constituent company template",
            "bse_profile": None,
            "nse_profile": None,
        },
    ])

    # Supplementary enrichment dataset (SRC-12)
    df_enrichment = pd.DataFrame([
        {
            "isin": "INE467B01029",
            "nse_symbol": "TCS",
            "bse_code": "532540",
            "company_name": "Tata Consultancy Services Ltd",
            "website": "https://new-enrichment-website.com",  # Should NOT overwrite primary!
            "about_company": "Enriched about text",          # Should NOT overwrite primary!
            "nse_profile": "https://www.nseindia.com/tcs",  # Should enrich since primary was None
        },
        {
            "isin": "INE009A01021",
            "nse_symbol": "INFY",
            "bse_code": "500209",
            "company_name": "Infosys Ltd",
            "website": "https://www.infosys.com",            # Should enrich missing website
            "about_company": "Leading IT services firm",     # Should replace template
            "nse_profile": "https://www.nseindia.com/infy",
        },
    ])

    lineage = []
    enriched, audit_logs = CompanyEnrichmentEngine.enrich_companies(df_companies, df_enrichment, lineage)

    # 1. TCS primary website & about must be preserved
    tcs_row = enriched[enriched["id"] == "TCS"].iloc[0]
    assert tcs_row["website"] == "https://www.tcs.com"
    assert tcs_row["about_company"] == "Primary about text"
    assert tcs_row["nse_profile"] == "https://www.nseindia.com/tcs"

    # 2. INFY missing website enriched
    infy_row = enriched[enriched["id"] == "INFY"].iloc[0]
    assert infy_row["website"] == "https://www.infosys.com"
    assert infy_row["about_company"] == "Leading IT services firm"
    assert infy_row["nse_profile"] == "https://www.nseindia.com/infy"

    # 3. Lineage recorded
    assert len(lineage) == 2
    assert len(audit_logs) == 2


def test_src12_matching_key_priority():
    """Verify 5-tier fallback matching priority (ISIN -> NSE -> BSE -> Ticker -> Name)."""
    df_companies = pd.DataFrame([
        {
            "id": "MARUTI",
            "company_name": "Maruti Suzuki India Ltd",
            "website": None,
            "bse_profile": "532500",
        }
    ])

    # Case A: Matches by NSE symbol
    df_enr_nse = pd.DataFrame([{
        "nse_symbol": "MARUTI",
        "company_name": "Different Name",
        "website": "https://maruti.com",
    }])
    enr_a, logs_a = CompanyEnrichmentEngine.enrich_companies(df_companies, df_enr_nse)
    assert logs_a[0]["match_strategy"] == "NSE_TICKER"

    # Case B: Matches by BSE code when NSE symbol absent
    df_enr_bse = pd.DataFrame([{
        "bse_code": "532500",
        "company_name": "Different Name",
        "website": "https://maruti.com",
    }])
    enr_b, logs_b = CompanyEnrichmentEngine.enrich_companies(df_companies, df_enr_bse)
    assert logs_b[0]["match_strategy"] == "BSE_CODE"

    # Case C: Matches by Normalized Company Name when codes absent
    df_enr_name = pd.DataFrame([{
        "company_name": "Maruti Suzuki India Ltd",
        "website": "https://maruti.com",
    }])
    enr_c, logs_c = CompanyEnrichmentEngine.enrich_companies(df_companies, df_enr_name)
    assert logs_c[0]["match_strategy"] == "NORMALIZED_NAME"


def test_manifest_and_table_mapping_generation(resolver, tmp_path):
    """Verify generation of output/source_manifest.csv and output/source_table_mapping.csv."""
    resolved = resolver.resolve_all_sources()

    manifest_file = tmp_path / "source_manifest.csv"
    table_mapping_file = tmp_path / "source_table_mapping.csv"

    # 1. Manifest
    ManifestGenerator.generate_source_manifest(resolved, manifest_file)
    assert manifest_file.exists()

    df_manifest = pd.read_csv(manifest_file)
    assert len(df_manifest) == 12
    assert "source_id" in df_manifest.columns
    assert "destination_table" in df_manifest.columns
    assert "rows_discovered" in df_manifest.columns
    assert set(df_manifest["mapping_status"]) == {"MAPPED"}

    # 2. Table mapping
    dummy_stats = [
        {
            "source_id": f"SRC-{i:02d}",
            "source_file": f"file_{i}.xlsx",
            "source_sheet": "Sheet1",
            "destination_table": "table_x",
            "rows_read": 100,
            "rows_valid": 100,
            "rows_rejected": 0,
            "mapping_status": "MAPPED",
        }
        for i in range(1, 13)
    ]
    ManifestGenerator.generate_source_table_mapping(dummy_stats, table_mapping_file)
    assert table_mapping_file.exists()

    df_table = pd.read_csv(table_mapping_file)
    assert len(df_table) == 12
    assert "source_id" in df_table.columns
    assert "rows_valid" in df_table.columns
