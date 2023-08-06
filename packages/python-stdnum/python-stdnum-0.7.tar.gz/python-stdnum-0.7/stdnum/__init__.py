# __init__.py - main module
# coding: utf-8
#
# Copyright (C) 2010, 2011, 2012 Arthur de Jong
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

"""Parse, validate and reformat standard numbers and codes.

This library offers functions for parsing, validating and reformatting
standard numbers and codes in various formats.

Currently this package supports the following formats:

 * UID (Umsatzsteuer-Identifikationsnummer, Austrian VAT number).
 * BTW, TVA, NWSt (Belgian VAT number).
 * EGN (ЕГН, Единен граждански номер, Bulgarian personal identity codes).
 * PNF (ЛНЧ, Личен номер на чужденец, Bulgarian number of a foreigner).
 * VAT (Идентификационен номер по ДДС, Bulgarian VAT number).
 * CPF (Cadastro de Pessoas Físicas, Brazillian national identifier).
 * Αριθμός Εγγραφής Φ.Π.Α. (Cypriot VAT number).
 * DIČ (Daňové identifikační číslo, Czech VAT number).
 * RČ (Rodné číslo, the Czech birth number).
 * Ust ID Nr. (Umsatzsteur Identifikationnummer, the German VAT number).
 * CPR (personnummer, the Danish citizen number).
 * CVR (Momsregistreringsnummer, Danish VAT number).
 * EAN (International Article Number).
 * KMKR (Käibemaksukohuslase, Estonian VAT number).
 * CIF (Certificado de Identificación Fiscal, Spanish company tax number).
 * DNI (Documento nacional de identidad, Spanish personal identity codes).
 * NIE (Número de Identificación de Extranjeros, Spanish foreigner number).
 * NIF (Número de Identificación Fiscal, Spanish VAT number).
 * VAT (European Union VAT number).
 * ALV nro (Arvonlisäveronumero, Finnish VAT number).
 * HETU (Henkilötunnus, Finnish personal identity code).
 * SIREN (a French company identification number).
 * n° TVA (taxe sur la valeur ajoutée, French VAT number).
 * VAT (United Kingdom (and Isle of Man) VAT registration number).
 * FPA, ΦΠΑ (Foros Prostithemenis Aksias, the Greek VAT number).
 * GRid (Global Release Identifier).
 * OIB (Osobni identifikacijski broj, Croatian identification number).
 * ANUM (Közösségi adószám, Hungarian VAT number).
 * IBAN (International Bank Account Number).
 * PPS No (Personal Public Service Number, Irish personal number).
 * VAT (Irish VAT number).
 * IMEI (International Mobile Equipment Identity).
 * IMSI (International Mobile Subscriber Identity).
 * ISAN (International Standard Audiovisual Number).
 * ISBN (International Standard Book Number).
 * ISIL (International Standard Identifier for Libraries).
 * ISMN (International Standard Music Number).
 * ISSN (International Standard Serial Number).
 * Partita IVA (Italian VAT number).
 * PVM (Pridėtinės vertės mokestis mokėtojo kodas, Lithuanian VAT number).
 * TVA (taxe sur la valeur ajoutée, Luxembourgian VAT number).
 * PVN (Pievienotās vērtības nodokļa, Latvian VAT number).
 * MEID (Mobile Equipment Identifier).
 * VAT (Maltese VAT number).
 * BSN (Burgerservicenummer, the Dutch national identification number).
 * BTW-nummer (Omzetbelastingnummer, the Dutch VAT number).
 * Onderwijsnummer (Dutch school number).
 * NIP (Numer Identyfikacji Podatkowej, Polish VAT number).
 * NIF (Número de identificação fiscal, Portuguese VAT number).
 * CF (Cod de înregistrare în scopuri de TVA, Romanian VAT number).
 * CNP (Cod Numeric Personal, Romanian Numerical Personal Code).
 * VAT (Moms, Mervärdesskatt, Swedish VAT number).
 * ID za DDV (Davčna številka, Slovenian VAT number).
 * IČ DPH (IČ pre daň z pridanej hodnoty, Slovak VAT number).
 * RČ (Rodné číslo, the Slovak birth number).
 * SSN (U.S. Social Security Number).

Furthermore a number of generic check digit algorithms are available:

 * the Verhoeff algorithm
 * the Luhn and Luhn mod N algorithms
 * some algorithms described in ISO/IEC 7064: Mod 11, 2, Mod 37, 2,
   Mod 97, 10, Mod 11, 10 and Mod 37, 36
"""

# the version number of the library
__version__ = '0.7'
