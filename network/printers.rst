Printer Setup
=============

**Configure System**:

- Driver:  Generic PostScript
- Address: ipp://prd-print-01.lustfield.net:631/postscript_p1

Model: HL-3290CDW
-----------------

print_driver/:

- Print Driver: ``Brother-HL-3400CN-pxlcolor.ppd`` OR ``Brother-HL-4070CDW-pxlcolor.ppd``
- Scanner Driver: ``brscan4-0.4.8-1.amd64.deb``

Notes:

- **Note to self**: Never buy a brother printer again... this is terrible
- `Firmware Updates
  <https://support.brother.com/g/b/downloadlist.aspx?c=us&lang=en&prod=hll3290cdw_us&os=10068>`__
- `Scanner
  <https://support.brother.com/g/b/downloadlist.aspx?c=us&lang=en&prod=hll3290cdw_us&os=128>`__

Download:

- Scanner driver 64bit (deb package)	
- Scan-key-tool 64bit (deb package)	

.. code-block:: sh

   dpkg -i brscan*
   brsaneconfig4 -a name=print80 model=HL-3290CDW ip=10.41.3.80

   apt install simple-scan
