#ifndef SRC_MESOMIE_HPP_
#define SRC_MESOMIE_HPP_
//******************************************************************************
//    Copyright (C) 2009-2022  Ovidio Pena <ovidio@bytesfall.com>
//    Copyright (C) 2013-2022  Konstantin Ladutenko <kostyfisik@gmail.com>
//
//    This file is part of scattnlay
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    The only additional remark is that we expect that all publications
//    describing work using this software, or all commercial products
//    using it, cite at least one of the following references:
//    [1] O. Pena and U. Pal, "Scattering of electromagnetic radiation by
//        a multilayered sphere," Computer Physics Communications,
//        vol. 180, Nov. 2009, pp. 2348-2354.
//    [2] K. Ladutenko, U. Pal, A. Rivera, and O. Pena-Rodriguez, "Mie
//        calculation of electromagnetic near-field for a multilayered
//        sphere," Computer Physics Communications, vol. 214, May 2017,
//        pp. 225-230.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//******************************************************************************

//******************************************************************************
// This class implements the algorithm for a multilayered sphere described by:
//    [1] W. Yang, "Improved recursive algorithm for light scattering by a
//        multilayered sphere,” Applied Optics, vol. 42, Mar. 2003, pp.
//        1710-1720.
//
// You can find the description of all the used equations in:
//    [2] O. Pena and U. Pal, "Scattering of electromagnetic radiation by
//        a multilayered sphere," Computer Physics Communications,
//        vol. 180, Nov. 2009, pp. 2348-2354.
//    [3] K. Ladutenko, U. Pal, A. Rivera, and O. Pena-Rodriguez, "Mie
//        calculation of electromagnetic near-field for a multilayered
//        sphere," Computer Physics Communications, vol. 214, May 2017,
//        pp. 225-230.
//
// Hereinafter all equations numbers refer to [2]
//******************************************************************************
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

#include "nmie.hpp"
#include "special-functions-impl.hpp"

namespace nmie {
//******************************************************************************
template <typename FloatType>
void MesoMie<FloatType>::calc_ab_classic(int nmax,
                                         FloatType x,
                                         std::complex<FloatType> m) {
  an_cl.resize(nmax + 1, static_cast<FloatType>(0.0));
  bn_cl.resize(nmax + 1, static_cast<FloatType>(0.0));
  std::vector<std::complex<FloatType>>         //
      Psi_mx(nmax + 1), Zeta_mx(nmax + 1),     //
      Psi_x(nmax + 1), Zeta_x(nmax + 1),       //
      D1_mx(nmax + 1), D3_mx(nmax + 1),        //
      D1_x(nmax + 1), D3_x(nmax + 1);          //
  evalPsiZetaD1D3(std::complex<FloatType>(x),  //
                  Psi_x, Zeta_x, D1_x, D3_x);  //
  evalPsiZetaD1D3(x * m,                       //
                  Psi_mx, Zeta_mx, D1_mx, D3_mx);
  for (int n = 0; n <= nmax; n++) {
    an_cl[n] = Psi_x[n] *
               (                           //
                   m * D1_x[n] - D1_mx[n]  //
                   ) /                     //
               Zeta_x[n] *
               (                           //
                   m * D3_x[n] - D1_mx[n]  //
               );
    bn_cl[n] = Psi_x[n] *
               (                           //
                   D1_x[n] - m * D1_mx[n]  //
                   ) /                     //
               Zeta_x[n] *
               (                           //
                   D3_x[n] - m * D1_mx[n]  //
               );                          //
  }
}

//******************************************************************************
template <typename FloatType>
void MesoMie<FloatType>::calc_ab(int nmax,
                                 FloatType R,
                                 std::complex<FloatType> xd,
                                 std::complex<FloatType> xm,
                                 std::complex<FloatType> eps_d,
                                 std::complex<FloatType> eps_m,
                                 std::complex<FloatType> d_parallel,
                                 std::complex<FloatType> d_perp) {
  an_.resize(nmax + 1, static_cast<FloatType>(0.0));
  bn_.resize(nmax + 1, static_cast<FloatType>(0.0));
  std::vector<std::complex<FloatType>>      //
      D1_xd(nmax + 1), D3_xd(nmax + 1),     //
      D1_xm(nmax + 1), D3_xm(nmax + 1),     //
      Psi_xd(nmax + 1), Zeta_xd(nmax + 1),  //
      Psi_xm(nmax + 1), Zeta_xm(nmax + 1);

  evalPsiZetaD1D3(std::complex<FloatType>(xd), Psi_xd, Zeta_xd, D1_xd, D3_xd);
  evalPsiZetaD1D3(std::complex<FloatType>(xm), Psi_xm, Zeta_xm, D1_xm, D3_xm);

  for (int n = 0; n <= nmax; n++) {
    an_[n] = Psi_xd[n] *
             (                                                           //
                 eps_m * xd * D1_xd[n] - eps_d * xm * D1_xm[n] +         //
                 (eps_m - eps_d) *                                       //
                     (                                                   //
                         static_cast<FloatType>(n * (n + 1)) * d_perp +  //
                         xd * D1_xd[n] * xm * D1_xm[n] * d_parallel      //
                         ) /                                             //
                     R                                                   //
                 ) /                                                     //
             Zeta_xd[n] *
             (                                                           //
                 eps_m * xd * D3_xd[n] - eps_d * xm * D1_xm[n] +         //
                 (eps_m - eps_d) *                                       //
                     (                                                   //
                         static_cast<FloatType>(n * (n + 1)) * d_perp +  //
                         xd * D3_xd[n] * xm * D1_xm[n] * d_parallel      //
                         ) /                                             //
                     R                                                   //
             );
    bn_[n] = Psi_xd[n] *
             (                                         //
                 xd * D1_xd[n] - xm * D1_xm[n] +       //
                 (xm * xm - xd * xd) * d_parallel / R  //
                 ) /                                   //
             Zeta_xd[n] *
             (                                         //
                 xd * D3_xd[n] - xm * D1_xm[n] +       //
                 (xm * xm - xd * xd) * d_parallel / R  //
             );                                        //
  }
}

}  // namespace nmie
#endif
