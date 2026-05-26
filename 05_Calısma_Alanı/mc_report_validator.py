#!/usr/bin/env python3
"""
MC Report Cross-Check Script v3 - Final Version
Comprehensive analysis of MC_KANIT_RAPORU.txt
"""

import re
import csv
from pathlib import Path
from typing import Dict, List, Optional

class MCReportParser:
    """Parse MC_KANIT_RAPORU.txt"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.sections = {}
        self.parse()

    def parse(self):
        """Parse the MC report file"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove Windows line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        lines = content.split('\n')

        current_section = None
        for i, line in enumerate(lines):
            line = line.strip()

            # Detect section headers: # SECTION NAME - X SATIR
            if line.startswith('#') and 'SATIR' in line and '- ' in line:
                match = re.search(r'#\s+(.+?)\s+-\s+\d+\s+SATIR', line)
                if match:
                    current_section = match.group(1).strip()
                    self.sections[current_section] = {'rows': [], 'mc_count': None, 'total_count': None}
                continue

            if not current_section:
                continue

            if not line:
                continue

            # Check for summary line
            if 'TOPLAM MC:' in line:
                match = re.search(r'TOPLAM MC:\s+(\d+)\s*/\s*(\d+)', line)
                if match:
                    self.sections[current_section]['mc_count'] = int(match.group(1))
                    self.sections[current_section]['total_count'] = int(match.group(2))
                continue

            # Skip separator lines
            if line.startswith('---') or line.startswith('='):
                continue

            # Parse data rows
            row = self.parse_row(line)
            if row:
                self.sections[current_section]['rows'].append(row)

    def parse_row(self, line: str) -> Optional[Dict]:
        """Parse a single data row"""
        # Pattern: feature In=X Out=Y Acc=... Sens=... Spec=... [<<<< MC]
        pattern = r'(\w+)\s+In=(\d+)\s+Out=(\d+)\s+Acc=([\d.]+)\s+Sens=([\d.]+)\s+Spec=([\d.]+|NA)\s*(<<<< MC)?'

        match = re.match(pattern, line)
        if match:
            feature, in_val, out_val, acc, sens, spec, mc_flag = match.groups()

            # Parse spec - could be NA or numeric
            spec_val = None
            if spec != 'NA':
                try:
                    spec_val = float(spec)
                except ValueError:
                    spec_val = None

            return {
                'feature': feature,
                'input': int(in_val),
                'output': int(out_val),
                'acc': float(acc),
                'sens': float(sens),
                'spec': spec_val,
                'spec_raw': spec,
                'mc_flagged': mc_flag is not None
            }
        return None


class CSVParser:
    """Parse CSV result files"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.rows = []
        self.parse()

    def parse(self):
        """Parse CSV file"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                parsed_row = {
                    'feature': row['Feature_Set'].strip('"'),
                    'input': int(row['Input']),
                    'output': int(row['Output']),
                    'acc': float(row['Mean_Acc']),
                    'sens': self.parse_value(row['Sens']),
                    'spec': self.parse_value(row['Spec']),
                }
                self.rows.append(parsed_row)

    @staticmethod
    def parse_value(val: str) -> Optional[float]:
        """Parse CSV value, handling NA"""
        val = val.strip()
        if val.upper() == 'NA':
            return None
        try:
            return float(val)
        except ValueError:
            return None


class CrossChecker:
    """Cross-check report against CSV files"""

    def __init__(self, report_path: str, csv_paths: Dict[str, str]):
        self.report = MCReportParser(report_path)
        self.csv_files = {name: CSVParser(path) for name, path in csv_paths.items()}
        self.findings = {
            'mc_flag_errors': [],
            'summary_mismatches': [],
            'data_mismatches': []
        }

    def run_all_checks(self):
        """Run all validation checks"""
        print("=" * 110)
        print("MC KANIT RAPORU CROSS-CHECK ANALYSIS")
        print("=" * 110)
        print(f"Report sections found: {len(self.report.sections)}\n")

        self.check_mc_flags()
        self.check_summaries()
        self.check_data_values()
        self.print_final_report()

    def check_mc_flags(self):
        """Check if MC flags are correct according to definition"""
        print("=" * 110)
        print("CHECK 1: MC FLAG CORRECTNESS")
        print("Definition: MC should be flagged when Sens=0 OR Spec=0 OR Spec=NA")
        print("=" * 110 + "\n")

        total_checked = 0
        total_errors = 0

        for section_name in sorted(self.report.sections.keys()):
            section_data = self.report.sections[section_name]
            if not section_data['rows']:
                continue

            total_checked += len(section_data['rows'])
            errors_in_section = []

            for report_row in section_data['rows']:
                # Determine if row SHOULD be flagged
                should_flag = (report_row['sens'] == 0 or report_row['spec'] == 0 or report_row['spec'] is None)
                is_flagged = report_row['mc_flagged']

                if should_flag != is_flagged:
                    total_errors += 1
                    status = "MISSING FLAG" if should_flag else "INCORRECTLY FLAGGED"
                    errors_in_section.append({
                        'row': f"{report_row['feature']} In={report_row['input']} Out={report_row['output']}",
                        'status': status,
                        'sens': report_row['sens'],
                        'spec': report_row['spec'],
                        'spec_raw': report_row['spec_raw'],
                        'is_flagged': is_flagged,
                        'should_flag': should_flag
                    })

            if errors_in_section:
                self.findings['mc_flag_errors'].append({
                    'section': section_name,
                    'errors': errors_in_section
                })
                print(f"✗ {section_name}")
                print(f"  {len(errors_in_section)} flag errors out of {len(section_data['rows'])} rows")
                for err in errors_in_section[:3]:
                    print(f"    {err['status']}: {err['row']}")
                    print(f"      Sens={err['sens']}, Spec={err['spec_raw']}, Flagged={err['is_flagged']}, Should be={err['should_flag']}")
                if len(errors_in_section) > 3:
                    print(f"    ... and {len(errors_in_section) - 3} more errors")
                print()
            else:
                print(f"✓ {section_name}: All {len(section_data['rows'])} MC flags correct\n")

        print(f"\nSUMMARY: {total_errors} MC flag errors out of {total_checked} rows checked\n")

    def check_summaries(self):
        """Check MC count summaries at end of sections"""
        print("=" * 110)
        print("CHECK 2: MC COUNT SUMMARIES")
        print("=" * 110 + "\n")

        total_summary_errors = 0

        for section_name in sorted(self.report.sections.keys()):
            section_data = self.report.sections[section_name]
            if not section_data['rows'] or section_data['mc_count'] is None:
                continue

            actual_count = sum(1 for row in section_data['rows'] if row['mc_flagged'])
            actual_total = len(section_data['rows'])
            reported_count = section_data['mc_count']
            reported_total = section_data['total_count']

            match_count = (reported_count == actual_count)
            match_total = (reported_total == actual_total)

            if not (match_count and match_total):
                total_summary_errors += 1
                self.findings['summary_mismatches'].append({
                    'section': section_name,
                    'reported': f"{reported_count}/{reported_total}",
                    'actual': f"{actual_count}/{actual_total}"
                })
                print(f"✗ {section_name}")
                print(f"  Reported: {reported_count}/{reported_total}")
                print(f"  Actual:   {actual_count}/{actual_total}\n")
            else:
                print(f"✓ {section_name}: {reported_count}/{reported_total} (correct)\n")

        if total_summary_errors == 0:
            print("SUMMARY: All MC count summaries are correct!\n")
        else:
            print(f"SUMMARY: {total_summary_errors} summary mismatches found\n")

    def check_data_values(self):
        """Check data values against CSV files"""
        print("=" * 110)
        print("CHECK 3: DATA VALUE VERIFICATION (THYAO dataset)")
        print("Checking Acc/Sens/Spec values against CSV files")
        print("=" * 110 + "\n")

        # Only check THYAO sections
        thyao_sections = {k: v for k, v in self.report.sections.items() if 'THYAO' in k}

        if not thyao_sections:
            print("No THYAO sections found in report\n")
            return

        tolerance = 0.0001
        total_data_errors = 0

        for section_name in sorted(thyao_sections.keys()):
            section_data = thyao_sections[section_name]
            csv_file = self.get_csv_for_section(section_name)

            if not csv_file:
                print(f"? {section_name}: No CSV file mapping\n")
                continue

            csv_data = self.csv_files[csv_file]
            errors_in_section = []

            for report_row in section_data['rows']:
                csv_row = self.find_csv_row(csv_data, report_row)

                if not csv_row:
                    errors_in_section.append({
                        'row': f"{report_row['feature']} In={report_row['input']} Out={report_row['output']}",
                        'issue': 'No matching row in CSV'
                    })
                    total_data_errors += 1
                    continue

                # Compare values with tolerance
                issues = []
                if abs(report_row['acc'] - csv_row['acc']) > tolerance:
                    issues.append(f"Acc: {report_row['acc']:.4f} vs {csv_row['acc']:.4f}")

                if report_row['sens'] is not None and csv_row['sens'] is not None:
                    if abs(report_row['sens'] - csv_row['sens']) > tolerance:
                        issues.append(f"Sens: {report_row['sens']:.4f} vs {csv_row['sens']:.4f}")

                if report_row['spec'] is not None and csv_row['spec'] is not None:
                    if abs(report_row['spec'] - csv_row['spec']) > tolerance:
                        issues.append(f"Spec: {report_row['spec']:.4f} vs {csv_row['spec']:.4f}")

                if issues:
                    total_data_errors += 1
                    errors_in_section.append({
                        'row': f"{report_row['feature']} In={report_row['input']} Out={report_row['output']}",
                        'issue': ', '.join(issues)
                    })

            if errors_in_section:
                self.findings['data_mismatches'].append({
                    'section': section_name,
                    'csv_file': csv_file,
                    'errors': errors_in_section
                })
                print(f"✗ {section_name} ({csv_file})")
                print(f"  {len(errors_in_section)} data mismatches out of {len(section_data['rows'])} rows")
                for err in errors_in_section[:3]:
                    print(f"    {err['row']}: {err['issue']}")
                if len(errors_in_section) > 3:
                    print(f"    ... and {len(errors_in_section) - 3} more mismatches")
                print()
            else:
                print(f"✓ {section_name} ({csv_file}): All values match!\n")

        print(f"SUMMARY: {total_data_errors} data value errors for THYAO dataset\n")

    @staticmethod
    def find_csv_row(csv_data, report_row) -> Optional[Dict]:
        """Find matching row in CSV"""
        for csv_row in csv_data.rows:
            if (csv_row['feature'] == report_row['feature'] and
                csv_row['input'] == report_row['input'] and
                csv_row['output'] == report_row['output']):
                return csv_row
        return None

    @staticmethod
    def get_csv_for_section(section_name: str) -> Optional[str]:
        """Map section name to CSV file"""
        if 'ESKI' in section_name and 'LSTM' in section_name:
            return 'lstm_old'
        elif 'ESKI' in section_name and 'CNN' in section_name:
            return 'cnn_old'
        elif 'GUNCEL' in section_name and 'LSTM' in section_name:
            return 'lstm_current'
        elif 'GUNCEL' in section_name and 'CNN' in section_name:
            return 'cnn_current'
        return None

    def print_final_report(self):
        """Print comprehensive final summary"""
        print("=" * 110)
        print("FINAL COMPREHENSIVE REPORT")
        print("=" * 110 + "\n")

        has_errors = False
        error_summary = []

        if self.findings['mc_flag_errors']:
            has_errors = True
            total_flag_errors = sum(len(f['errors']) for f in self.findings['mc_flag_errors'])
            error_summary.append(f"MC Flag Errors: {total_flag_errors} in {len(self.findings['mc_flag_errors'])} sections")

        if self.findings['summary_mismatches']:
            has_errors = True
            error_summary.append(f"Summary Mismatches: {len(self.findings['summary_mismatches'])} sections")

        if self.findings['data_mismatches']:
            has_errors = True
            total_data_errors = sum(len(f['errors']) for f in self.findings['data_mismatches'])
            error_summary.append(f"Data Value Mismatches: {total_data_errors} in {len(self.findings['data_mismatches'])} sections")

        if not has_errors:
            print("✓✓✓ ALL CHECKS PASSED ✓✓✓")
            print("\nThe MC report is fully consistent and accurate!")
            print("- All MC flags are correct (flagged when Sens=0 or Spec=0 or Spec=NA)")
            print("- All summary counts match actual flag counts")
            print("- All THYAO data values match CSV files")
        else:
            print("✗ ERRORS DETECTED:\n")
            for summary in error_summary:
                print(f"  • {summary}")
            print("\nSee detailed findings above for specific issues.")

        print("\n" + "=" * 110)


def main():
    report_path = "/sessions/admiring-brave-thompson/mnt/PROJE_ALL/Literatür+Kodlar/MC_KANIT_RAPORU.txt"

    csv_paths = {
        'lstm_current': "/sessions/admiring-brave-thompson/mnt/PROJE_ALL/2018-2026 çıktılar/LSTM_sonuclar_FINAL.csv",
        'cnn_current': "/sessions/admiring-brave-thompson/mnt/PROJE_ALL/2018-2026 çıktılar/CNN_sonuclar_FINAL.csv",
        'lstm_old': "/sessions/admiring-brave-thompson/mnt/PROJE_ALL/2018-2022 çıktılar/LSTM_sonuclar_FINAL_eski.csv",
        'cnn_old': "/sessions/admiring-brave-thompson/mnt/PROJE_ALL/2018-2022 çıktılar/CNN_sonuclar_FINAL_eski.csv",
    }

    # Verify files exist
    print("Verifying files...\n")
    if not Path(report_path).exists():
        print(f"✗ Report not found: {report_path}")
        return

    for name, path in csv_paths.items():
        if not Path(path).exists():
            print(f"✗ CSV file not found ({name}): {path}")
            return

    print("✓ All files verified\n")

    # Run cross-check
    checker = CrossChecker(report_path, csv_paths)
    checker.run_all_checks()


if __name__ == '__main__':
    main()
