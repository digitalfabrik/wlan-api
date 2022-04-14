import itertools
import subprocess
import tempfile

PDFJAM_BIN = "/usr/bin/pdfjam"


def merge_final_pdf(voucher_buffer, voucher_count, ads_file):
    with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as ads_file_output:
        ads_file.save(ads_file_output)
        ads_file_output.flush()

        with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as output:
            output.write(buffer_pdf_to_2x2(voucher_buffer))
            output.flush()

            return shuffle_ads(ads_file_output.name, output.name, int(voucher_count / 4))  # /4 Because of 2x2 nup


def shuffle_ads(ads_file_path, voucher_pdf_path, voucher_pdf_pages):
    page_with_ads = 1

    pdfjam_pages = [
        [voucher_pdf_path, str(i + 1), ads_file_path,
         str(page_with_ads)] for i in range(voucher_pdf_pages)]

    process = subprocess.Popen(
        [PDFJAM_BIN, *list(itertools.chain(*pdfjam_pages)), "--outfile", "/dev/stdout", "--paper", "a4paper",
         "--rotateoversize",
         "false"],
        shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = process.communicate()

    if stderrdata is not None:
        return None

    return stdoutdata


def buffer_pdf_to_2x2(voucher_buffer):
    process = subprocess.Popen([PDFJAM_BIN, "--nup", "2x2", "--outfile", "/dev/stdout", "--"], shell=False,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = process.communicate(input=voucher_buffer.getvalue())

    if stderrdata is not None:
        return None, None

    return stdoutdata
