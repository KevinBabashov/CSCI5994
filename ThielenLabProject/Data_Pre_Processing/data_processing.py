from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent


def run_fastp(
    r1_in,
    r1_out,
    r2_in=None,
    r2_out=None,
    html="fastp.html",
    json="fastp.json",
    threads=4,
    detect_adapter=True,
    extra_args=None,
):
    r1_in = Path(r1_in)
    r1_out = Path(r1_out)
    html = Path(html)
    json = Path(json)

    if not r1_in.exists():
        raise FileNotFoundError(f"Input file not found: {r1_in}")

    cmd = [
        "fastp",
        "-i", str(r1_in),
        "-o", str(r1_out),
        "-h", str(html),
        "-j", str(json),
        "-w", str(threads),
    ]

    if r2_in is not None and r2_out is not None:
        r2_in = Path(r2_in)
        r2_out = Path(r2_out)

        if not r2_in.exists():
            raise FileNotFoundError(f"R2 input file not found: {r2_in}")

        cmd.extend(["-I", str(r2_in), "-O", str(r2_out)])

        if detect_adapter:
            cmd.append("--detect_adapter_for_pe")

    if extra_args:
        cmd.extend(extra_args)

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    run_fastp(
        r1_in=BASE / "FAZ39948_pass_barcode01_c45a1349_2880b1cb_0.fastq.gz",
        r1_out=BASE / "FAZ39948_pass_barcode01_c45a1349_2880b1cb_0.cleaned.fastq.gz",
        html=BASE / "fastp.html",
        json=BASE / "fastp.json",
        threads=8,
        extra_args=["-q", "20", "-l", "50"],
    )


if __name__ == "__main__":
    main()
