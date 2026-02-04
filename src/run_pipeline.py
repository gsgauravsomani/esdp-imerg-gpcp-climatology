from src.concatenate_imerg import main as concatenate_imerg_main
from src.unit_convert_imerg import main as unit_convert_imerg_main
from src.extract_gpcp import main as extract_gpcp_main
from src.regrid_imerg_to_gpcp import main as regrid_main
from src.sanity_check_regrid import main as sanity_check_main


def main():
    print("[1/5] Concatenating IMERG monthly files...")
    concatenate_imerg_main()

    print("[2/5] Converting IMERG units to mm/day...")
    unit_convert_imerg_main()

    print("[3/5] Extracting GPCP subset...")
    extract_gpcp_main()

    print("[4/5] Regridding IMERG to GPCP grid...")
    regrid_main()

    print("[5/5] Running sanity checks...")
    sanity_check_main()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
