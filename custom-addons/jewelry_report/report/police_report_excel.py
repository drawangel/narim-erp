import base64
from io import BytesIO

import xlsxwriter


class PoliceReportExcel:
    """Generator for police report Excel file.

    IMPORTANT: The header row is NOT editable. It must be generated
    EXACTLY as specified because police use parsers/automations to
    process the file.
    """

    # Exact headers required by Mossos d'Esquadra - DO NOT MODIFY
    HEADERS = [
        'Nº CONTRACTE',
        'NOM I COGNOMS',
        'DNI',
        'DATA COMPRA',
        'ESTABLIMENT',
        'TIPUS',
        'DESCRIPCIÓ',
        'S/N - INSCRIPCIONS',
    ]

    def generate(self, lines_data):
        """Generate the Excel file with the exact required header.

        Args:
            lines_data: List of dicts with keys:
                - contract_number
                - client_name
                - dni
                - purchase_date (formatted as DD/MM/YYYY)
                - store
                - jewelry_type
                - description
                - inscriptions

        Returns:
            Base64 encoded Excel file content
        """
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Informe Policial')

        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })

        # Data format
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        # Column widths (approximate based on content)
        column_widths = [15, 30, 12, 12, 25, 15, 40, 25]
        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)

        # Write header row (row 0) - EXACT format required
        for col, header in enumerate(self.HEADERS):
            worksheet.write(0, col, header, header_format)

        # Write data rows (starting from row 1)
        for row, line in enumerate(lines_data, start=1):
            worksheet.write(row, 0, line.get('contract_number', ''), data_format)
            worksheet.write(row, 1, line.get('client_name', ''), data_format)
            worksheet.write(row, 2, line.get('dni', ''), data_format)
            worksheet.write(row, 3, line.get('purchase_date', ''), data_format)
            worksheet.write(row, 4, line.get('store', ''), data_format)
            worksheet.write(row, 5, line.get('jewelry_type', ''), data_format)
            worksheet.write(row, 6, line.get('description', ''), data_format)
            # Default to 'SN INSCRIPCIONS' if no inscriptions
            inscriptions = line.get('inscriptions') or 'SN INSCRIPCIONS'
            worksheet.write(row, 7, inscriptions, data_format)

        # Freeze header row
        worksheet.freeze_panes(1, 0)

        # Auto-filter for easy filtering
        if lines_data:
            worksheet.autofilter(0, 0, len(lines_data), len(self.HEADERS) - 1)

        workbook.close()
        output.seek(0)
        return base64.b64encode(output.read())
