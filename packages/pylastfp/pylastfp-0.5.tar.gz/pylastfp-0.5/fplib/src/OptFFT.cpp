/***************************************************************************
* This file is part of last.fm fingerprint app                             *
*  Last.fm Ltd <mir@last.fm>                                               *
*                                                                          *
* This library is free software; you can redistribute it and/or            *
* modify it under the terms of the GNU Lesser General Public               *
* License as published by the Free Software Foundation; either             *
* version 2.1 of the License, or (at your option) any later version.       *
*                                                                          *
* This library is distributed in the hope that it will be useful,          *
* but WITHOUT ANY WARRANTY; without even the implied warranty of           *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU        *
* Lesser General Public License for more details.                          *
*                                                                          *
* You should have received a copy of the GNU Lesser General Public         *
* License along with this library; if not, write to the Free Software      *
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 *
* USA                                                                      *
*                                                                          *
* Part of this code is based on the work of Y. Ke, D. Hoiem, and           *
* R. Sukthankar - "Computer Vision for Music Identification",              *
* in Proceedings of Computer Vision and Pattern Recognition, 2005.         *
* See also http://www.cs.cmu.edu/~yke/musicretrieval/                      *
***************************************************************************/

#include "OptFFT.h"
#include "fp_helper_fun.h"
#include "Filter.h" // for NBANDS

#include <cmath>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <cstdlib> 
#include <stdexcept>
#include <cstring>

using namespace std;
// ----------------------------------------------------------------------

namespace fingerprint
{

   static const float hann[] = {
      0.000000f,0.000002f,0.000009f,0.000021f,0.000038f,0.000059f,0.000085f,0.000115f,0.000151f,0.000191f,0.000236f,
      0.000285f,0.000339f,0.000398f,0.000462f,0.000530f,0.000603f,0.000681f,0.000763f,0.000850f,0.000942f,0.001038f,
      0.001140f,0.001245f,0.001356f,0.001471f,0.001591f,0.001716f,0.001845f,0.001980f,0.002118f,0.002262f,0.002410f,
      0.002563f,0.002720f,0.002883f,0.003049f,0.003221f,0.003397f,0.003578f,0.003764f,0.003954f,0.004149f,0.004349f,
      0.004553f,0.004762f,0.004976f,0.005194f,0.005417f,0.005645f,0.005877f,0.006114f,0.006355f,0.006602f,0.006853f,
      0.007108f,0.007368f,0.007633f,0.007903f,0.008177f,0.008455f,0.008739f,0.009027f,0.009319f,0.009617f,0.009919f,
      0.010225f,0.010536f,0.010852f,0.011172f,0.011497f,0.011827f,0.012161f,0.012499f,0.012843f,0.013191f,0.013543f,
      0.013900f,0.014262f,0.014628f,0.014999f,0.015374f,0.015754f,0.016139f,0.016528f,0.016921f,0.017320f,0.017722f,
      0.018130f,0.018541f,0.018958f,0.019379f,0.019804f,0.020234f,0.020668f,0.021107f,0.021551f,0.021999f,0.022451f,
      0.022908f,0.023370f,0.023836f,0.024306f,0.024781f,0.025260f,0.025744f,0.026233f,0.026725f,0.027223f,0.027724f,
      0.028231f,0.028741f,0.029256f,0.029776f,0.030300f,0.030828f,0.031361f,0.031898f,0.032440f,0.032986f,0.033536f,
      0.034091f,0.034650f,0.035214f,0.035781f,0.036354f,0.036930f,0.037512f,0.038097f,0.038687f,0.039281f,0.039879f,
      0.040482f,0.041089f,0.041701f,0.042316f,0.042936f,0.043561f,0.044189f,0.044822f,0.045460f,0.046101f,0.046747f,
      0.047397f,0.048052f,0.048710f,0.049373f,0.050040f,0.050711f,0.051387f,0.052067f,0.052751f,0.053439f,0.054132f,
      0.054828f,0.055529f,0.056234f,0.056943f,0.057657f,0.058374f,0.059096f,0.059822f,0.060552f,0.061286f,0.062024f,
      0.062767f,0.063513f,0.064264f,0.065019f,0.065777f,0.066540f,0.067307f,0.068078f,0.068854f,0.069633f,0.070416f,
      0.071204f,0.071995f,0.072790f,0.073590f,0.074393f,0.075201f,0.076012f,0.076828f,0.077647f,0.078470f,0.079298f,
      0.080129f,0.080964f,0.081804f,0.082647f,0.083494f,0.084345f,0.085200f,0.086059f,0.086922f,0.087788f,0.088659f,
      0.089533f,0.090412f,0.091294f,0.092180f,0.093070f,0.093963f,0.094861f,0.095762f,0.096667f,0.097576f,0.098489f,
      0.099406f,0.100326f,0.101250f,0.102178f,0.103109f,0.104045f,0.104984f,0.105926f,0.106873f,0.107823f,0.108777f,
      0.109734f,0.110696f,0.111661f,0.112629f,0.113601f,0.114577f,0.115557f,0.116540f,0.117526f,0.118517f,0.119511f,
      0.120508f,0.121509f,0.122514f,0.123522f,0.124534f,0.125549f,0.126568f,0.127590f,0.128616f,0.129645f,0.130678f,
      0.131714f,0.132754f,0.133797f,0.134844f,0.135894f,0.136948f,0.138005f,0.139065f,0.140129f,0.141196f,0.142266f,
      0.143340f,0.144418f,0.145498f,0.146582f,0.147670f,0.148760f,0.149854f,0.150951f,0.152052f,0.153156f,0.154263f,
      0.155373f,0.156487f,0.157603f,0.158723f,0.159847f,0.160973f,0.162103f,0.163236f,0.164372f,0.165511f,0.166653f,
      0.167799f,0.168947f,0.170099f,0.171254f,0.172411f,0.173572f,0.174737f,0.175904f,0.177074f,0.178247f,0.179423f,
      0.180603f,0.181785f,0.182970f,0.184158f,0.185350f,0.186544f,0.187741f,0.188941f,0.190144f,0.191350f,0.192559f,
      0.193771f,0.194986f,0.196203f,0.197423f,0.198647f,0.199873f,0.201102f,0.202333f,0.203568f,0.204805f,0.206045f,
      0.207288f,0.208534f,0.209782f,0.211033f,0.212287f,0.213544f,0.214803f,0.216065f,0.217329f,0.218597f,0.219867f,
      0.221139f,0.222414f,0.223692f,0.224972f,0.226255f,0.227541f,0.228829f,0.230120f,0.231413f,0.232709f,0.234007f,
      0.235308f,0.236611f,0.237917f,0.239225f,0.240536f,0.241849f,0.243165f,0.244483f,0.245803f,0.247126f,0.248451f,
      0.249779f,0.251108f,0.252441f,0.253775f,0.255112f,0.256451f,0.257793f,0.259137f,0.260483f,0.261831f,0.263182f,
      0.264534f,0.265889f,0.267247f,0.268606f,0.269967f,0.271331f,0.272697f,0.274065f,0.275435f,0.276808f,0.278182f,
      0.279558f,0.280937f,0.282318f,0.283700f,0.285085f,0.286472f,0.287861f,0.289251f,0.290644f,0.292039f,0.293435f,
      0.294834f,0.296235f,0.297637f,0.299041f,0.300448f,0.301856f,0.303266f,0.304678f,0.306091f,0.307507f,0.308924f,
      0.310343f,0.311764f,0.313187f,0.314611f,0.316038f,0.317466f,0.318895f,0.320327f,0.321760f,0.323194f,0.324631f,
      0.326069f,0.327509f,0.328950f,0.330393f,0.331837f,0.333283f,0.334731f,0.336180f,0.337631f,0.339083f,0.340537f,
      0.341993f,0.343449f,0.344908f,0.346368f,0.347829f,0.349291f,0.350755f,0.352221f,0.353688f,0.355156f,0.356626f,
      0.358097f,0.359569f,0.361042f,0.362517f,0.363994f,0.365471f,0.366950f,0.368430f,0.369911f,0.371394f,0.372877f,
      0.374362f,0.375848f,0.377336f,0.378824f,0.380314f,0.381804f,0.383296f,0.384789f,0.386283f,0.387778f,0.389274f,
      0.390771f,0.392269f,0.393768f,0.395269f,0.396770f,0.398272f,0.399775f,0.401279f,0.402784f,0.404290f,0.405797f,
      0.407305f,0.408813f,0.410322f,0.411833f,0.413344f,0.414856f,0.416368f,0.417882f,0.419396f,0.420911f,0.422427f,
      0.423944f,0.425461f,0.426979f,0.428497f,0.430017f,0.431537f,0.433057f,0.434578f,0.436100f,0.437623f,0.439146f,
      0.440669f,0.442193f,0.443718f,0.445243f,0.446769f,0.448295f,0.449822f,0.451349f,0.452877f,0.454405f,0.455934f,
      0.457463f,0.458992f,0.460522f,0.462052f,0.463582f,0.465113f,0.466644f,0.468176f,0.469708f,0.471240f,0.472772f,
      0.474305f,0.475837f,0.477370f,0.478904f,0.480437f,0.481971f,0.483505f,0.485039f,0.486573f,0.488107f,0.489641f,
      0.491176f,0.492710f,0.494245f,0.495780f,0.497314f,0.498849f,0.500384f,0.501918f,0.503453f,0.504988f,0.506522f,
      0.508057f,0.509591f,0.511126f,0.512660f,0.514194f,0.515728f,0.517262f,0.518796f,0.520330f,0.521863f,0.523396f,
      0.524929f,0.526462f,0.527994f,0.529526f,0.531058f,0.532590f,0.534121f,0.535652f,0.537183f,0.538713f,0.540243f,
      0.541773f,0.543302f,0.544831f,0.546359f,0.547887f,0.549414f,0.550941f,0.552468f,0.553994f,0.555519f,0.557044f,
      0.558569f,0.560093f,0.561616f,0.563139f,0.564661f,0.566182f,0.567703f,0.569223f,0.570743f,0.572262f,0.573780f,
      0.575298f,0.576815f,0.578331f,0.579846f,0.581361f,0.582875f,0.584388f,0.585900f,0.587412f,0.588922f,0.590432f,
      0.591941f,0.593449f,0.594957f,0.596463f,0.597968f,0.599473f,0.600977f,0.602479f,0.603981f,0.605482f,0.606981f,
      0.608480f,0.609978f,0.611474f,0.612970f,0.614464f,0.615958f,0.617450f,0.618941f,0.620431f,0.621920f,0.623408f,
      0.624895f,0.626380f,0.627865f,0.629348f,0.630830f,0.632310f,0.633790f,0.635268f,0.636745f,0.638220f,0.639695f,
      0.641167f,0.642639f,0.644109f,0.645578f,0.647046f,0.648512f,0.649977f,0.651440f,0.652902f,0.654363f,0.655822f,
      0.657279f,0.658735f,0.660190f,0.661643f,0.663094f,0.664544f,0.665993f,0.667440f,0.668885f,0.670329f,0.671771f,
      0.673212f,0.674650f,0.676088f,0.677523f,0.678957f,0.680389f,0.681820f,0.683249f,0.684676f,0.686101f,0.687525f,
      0.688946f,0.690366f,0.691785f,0.693201f,0.694616f,0.696029f,0.697439f,0.698849f,0.700256f,0.701661f,0.703065f,
      0.704466f,0.705866f,0.707263f,0.708659f,0.710053f,0.711444f,0.712834f,0.714222f,0.715608f,0.716991f,0.718373f,
      0.719752f,0.721130f,0.722505f,0.723879f,0.725250f,0.726619f,0.727986f,0.729351f,0.730714f,0.732074f,0.733432f,
      0.734788f,0.736142f,0.737494f,0.738843f,0.740191f,0.741536f,0.742878f,0.744219f,0.745557f,0.746892f,0.748226f,
      0.749557f,0.750886f,0.752212f,0.753536f,0.754857f,0.756177f,0.757493f,0.758808f,0.760120f,0.761429f,0.762736f,
      0.764041f,0.765343f,0.766642f,0.767939f,0.769234f,0.770526f,0.771815f,0.773102f,0.774386f,0.775668f,0.776947f,
      0.778224f,0.779497f,0.780769f,0.782037f,0.783303f,0.784567f,0.785827f,0.787085f,0.788340f,0.789593f,0.790842f,
      0.792089f,0.793334f,0.794575f,0.795814f,0.797050f,0.798283f,0.799513f,0.800741f,0.801965f,0.803187f,0.804406f,
      0.805622f,0.806835f,0.808046f,0.809253f,0.810458f,0.811659f,0.812858f,0.814054f,0.815246f,0.816436f,0.817623f,
      0.818807f,0.819987f,0.821165f,0.822340f,0.823512f,0.824680f,0.825846f,0.827008f,0.828168f,0.829324f,0.830477f,
      0.831628f,0.832775f,0.833918f,0.835059f,0.836197f,0.837331f,0.838462f,0.839591f,0.840715f,0.841837f,0.842955f,
      0.844071f,0.845183f,0.846291f,0.847397f,0.848499f,0.849598f,0.850693f,0.851786f,0.852874f,0.853960f,0.855042f,
      0.856121f,0.857197f,0.858269f,0.859338f,0.860404f,0.861466f,0.862524f,0.863580f,0.864631f,0.865680f,0.866725f,
      0.867766f,0.868804f,0.869839f,0.870870f,0.871897f,0.872922f,0.873942f,0.874959f,0.875973f,0.876983f,0.877989f,
      0.878992f,0.879991f,0.880987f,0.881979f,0.882967f,0.883952f,0.884934f,0.885911f,0.886885f,0.887856f,0.888822f,
      0.889785f,0.890745f,0.891701f,0.892653f,0.893601f,0.894545f,0.895486f,0.896423f,0.897357f,0.898287f,0.899213f,
      0.900135f,0.901053f,0.901968f,0.902879f,0.903786f,0.904689f,0.905588f,0.906484f,0.907376f,0.908264f,0.909148f,
      0.910028f,0.910904f,0.911777f,0.912645f,0.913510f,0.914371f,0.915228f,0.916081f,0.916930f,0.917775f,0.918616f,
      0.919454f,0.920287f,0.921116f,0.921942f,0.922763f,0.923581f,0.924394f,0.925204f,0.926009f,0.926810f,0.927608f,
      0.928401f,0.929191f,0.929976f,0.930757f,0.931534f,0.932308f,0.933077f,0.933842f,0.934603f,0.935359f,0.936112f,
      0.936861f,0.937605f,0.938345f,0.939082f,0.939814f,0.940542f,0.941265f,0.941985f,0.942701f,0.943412f,0.944119f,
      0.944822f,0.945521f,0.946215f,0.946906f,0.947592f,0.948274f,0.948951f,0.949625f,0.950294f,0.950959f,0.951620f,
      0.952276f,0.952928f,0.953576f,0.954220f,0.954859f,0.955495f,0.956125f,0.956752f,0.957374f,0.957992f,0.958606f,
      0.959215f,0.959820f,0.960420f,0.961017f,0.961609f,0.962196f,0.962780f,0.963358f,0.963933f,0.964503f,0.965069f,
      0.965630f,0.966187f,0.966740f,0.967288f,0.967832f,0.968371f,0.968906f,0.969437f,0.969963f,0.970485f,0.971002f,
      0.971515f,0.972023f,0.972527f,0.973027f,0.973522f,0.974012f,0.974498f,0.974980f,0.975457f,0.975930f,0.976398f,
      0.976862f,0.977321f,0.977776f,0.978226f,0.978672f,0.979113f,0.979549f,0.979982f,0.980409f,0.980832f,0.981251f,
      0.981665f,0.982075f,0.982480f,0.982880f,0.983276f,0.983667f,0.984054f,0.984436f,0.984814f,0.985187f,0.985556f,
      0.985919f,0.986279f,0.986634f,0.986984f,0.987329f,0.987670f,0.988007f,0.988339f,0.988666f,0.988989f,0.989307f,
      0.989620f,0.989929f,0.990233f,0.990532f,0.990827f,0.991118f,0.991403f,0.991684f,0.991961f,0.992233f,0.992500f,
      0.992762f,0.993020f,0.993273f,0.993522f,0.993766f,0.994005f,0.994240f,0.994470f,0.994695f,0.994916f,0.995132f,
      0.995343f,0.995550f,0.995752f,0.995949f,0.996142f,0.996329f,0.996513f,0.996691f,0.996865f,0.997035f,0.997199f,
      0.997359f,0.997514f,0.997665f,0.997810f,0.997952f,0.998088f,0.998220f,0.998347f,0.998469f,0.998587f,0.998700f,
      0.998808f,0.998912f,0.999010f,0.999105f,0.999194f,0.999279f,0.999359f,0.999434f,0.999505f,0.999571f,0.999632f,
      0.999689f,0.999740f,0.999787f,0.999830f,0.999868f,0.999900f,0.999929f,0.999952f,0.999971f,0.999985f,0.999995f,
      0.999999f,0.999999f,0.999995f,0.999985f,0.999971f,0.999952f,0.999929f,0.999900f,0.999868f,0.999830f,0.999787f,
      0.999740f,0.999689f,0.999632f,0.999571f,0.999505f,0.999434f,0.999359f,0.999279f,0.999194f,0.999105f,0.999010f,
      0.998912f,0.998808f,0.998700f,0.998587f,0.998469f,0.998347f,0.998220f,0.998088f,0.997952f,0.997810f,0.997665f,
      0.997514f,0.997359f,0.997199f,0.997035f,0.996865f,0.996691f,0.996513f,0.996329f,0.996142f,0.995949f,0.995752f,
      0.995550f,0.995343f,0.995132f,0.994916f,0.994695f,0.994470f,0.994240f,0.994005f,0.993766f,0.993522f,0.993273f,
      0.993020f,0.992762f,0.992500f,0.992233f,0.991961f,0.991684f,0.991403f,0.991118f,0.990827f,0.990532f,0.990233f,
      0.989929f,0.989620f,0.989307f,0.988989f,0.988666f,0.988339f,0.988007f,0.987670f,0.987329f,0.986984f,0.986634f,
      0.986279f,0.985919f,0.985556f,0.985187f,0.984814f,0.984436f,0.984054f,0.983667f,0.983276f,0.982880f,0.982480f,
      0.982075f,0.981665f,0.981251f,0.980832f,0.980409f,0.979982f,0.979549f,0.979113f,0.978672f,0.978226f,0.977776f,
      0.977321f,0.976862f,0.976398f,0.975930f,0.975457f,0.974980f,0.974498f,0.974012f,0.973522f,0.973027f,0.972527f,
      0.972023f,0.971515f,0.971002f,0.970485f,0.969963f,0.969437f,0.968906f,0.968371f,0.967832f,0.967288f,0.966740f,
      0.966187f,0.965630f,0.965069f,0.964503f,0.963933f,0.963358f,0.962780f,0.962196f,0.961609f,0.961017f,0.960420f,
      0.959820f,0.959215f,0.958606f,0.957992f,0.957374f,0.956752f,0.956125f,0.955495f,0.954859f,0.954220f,0.953576f,
      0.952928f,0.952276f,0.951620f,0.950959f,0.950294f,0.949625f,0.948951f,0.948274f,0.947592f,0.946906f,0.946215f,
      0.945521f,0.944822f,0.944119f,0.943412f,0.942701f,0.941985f,0.941265f,0.940542f,0.939814f,0.939082f,0.938345f,
      0.937605f,0.936861f,0.936112f,0.935359f,0.934603f,0.933842f,0.933077f,0.932308f,0.931534f,0.930757f,0.929976f,
      0.929191f,0.928401f,0.927608f,0.926810f,0.926009f,0.925204f,0.924394f,0.923581f,0.922763f,0.921942f,0.921116f,
      0.920287f,0.919454f,0.918616f,0.917775f,0.916930f,0.916081f,0.915228f,0.914371f,0.913510f,0.912645f,0.911777f,
      0.910904f,0.910028f,0.909148f,0.908264f,0.907376f,0.906484f,0.905588f,0.904689f,0.903786f,0.902879f,0.901968f,
      0.901053f,0.900135f,0.899213f,0.898287f,0.897357f,0.896423f,0.895486f,0.894545f,0.893601f,0.892653f,0.891701f,
      0.890745f,0.889785f,0.888822f,0.887856f,0.886885f,0.885911f,0.884934f,0.883952f,0.882967f,0.881979f,0.880987f,
      0.879991f,0.878992f,0.877989f,0.876983f,0.875973f,0.874959f,0.873942f,0.872922f,0.871897f,0.870870f,0.869839f,
      0.868804f,0.867766f,0.866725f,0.865680f,0.864631f,0.863580f,0.862524f,0.861466f,0.860404f,0.859338f,0.858269f,
      0.857197f,0.856121f,0.855042f,0.853960f,0.852874f,0.851786f,0.850693f,0.849598f,0.848499f,0.847397f,0.846291f,
      0.845183f,0.844071f,0.842955f,0.841837f,0.840715f,0.839591f,0.838462f,0.837331f,0.836197f,0.835059f,0.833918f,
      0.832775f,0.831628f,0.830477f,0.829324f,0.828168f,0.827008f,0.825846f,0.824680f,0.823512f,0.822340f,0.821165f,
      0.819987f,0.818807f,0.817623f,0.816436f,0.815246f,0.814054f,0.812858f,0.811659f,0.810458f,0.809253f,0.808046f,
      0.806835f,0.805622f,0.804406f,0.803187f,0.801965f,0.800741f,0.799513f,0.798283f,0.797050f,0.795814f,0.794575f,
      0.793334f,0.792089f,0.790842f,0.789593f,0.788340f,0.787085f,0.785827f,0.784567f,0.783303f,0.782037f,0.780769f,
      0.779497f,0.778224f,0.776947f,0.775668f,0.774386f,0.773102f,0.771815f,0.770526f,0.769234f,0.767939f,0.766642f,
      0.765343f,0.764041f,0.762736f,0.761429f,0.760120f,0.758808f,0.757493f,0.756177f,0.754857f,0.753536f,0.752212f,
      0.750886f,0.749557f,0.748226f,0.746892f,0.745557f,0.744219f,0.742878f,0.741536f,0.740191f,0.738843f,0.737494f,
      0.736142f,0.734788f,0.733432f,0.732074f,0.730714f,0.729351f,0.727986f,0.726619f,0.725250f,0.723879f,0.722505f,
      0.721130f,0.719752f,0.718373f,0.716991f,0.715608f,0.714222f,0.712834f,0.711444f,0.710053f,0.708659f,0.707263f,
      0.705866f,0.704466f,0.703065f,0.701661f,0.700256f,0.698849f,0.697439f,0.696029f,0.694616f,0.693201f,0.691785f,
      0.690366f,0.688946f,0.687525f,0.686101f,0.684676f,0.683249f,0.681820f,0.680389f,0.678957f,0.677523f,0.676088f,
      0.674650f,0.673212f,0.671771f,0.670329f,0.668885f,0.667440f,0.665993f,0.664544f,0.663094f,0.661643f,0.660190f,
      0.658735f,0.657279f,0.655822f,0.654363f,0.652902f,0.651440f,0.649977f,0.648512f,0.647046f,0.645578f,0.644109f,
      0.642639f,0.641167f,0.639695f,0.638220f,0.636745f,0.635268f,0.633790f,0.632310f,0.630830f,0.629348f,0.627865f,
      0.626380f,0.624895f,0.623408f,0.621920f,0.620431f,0.618941f,0.617450f,0.615958f,0.614464f,0.612970f,0.611474f,
      0.609978f,0.608480f,0.606981f,0.605482f,0.603981f,0.602479f,0.600977f,0.599473f,0.597968f,0.596463f,0.594957f,
      0.593449f,0.591941f,0.590432f,0.588922f,0.587412f,0.585900f,0.584388f,0.582875f,0.581361f,0.579846f,0.578331f,
      0.576815f,0.575298f,0.573780f,0.572262f,0.570743f,0.569223f,0.567703f,0.566182f,0.564661f,0.563139f,0.561616f,
      0.560093f,0.558569f,0.557044f,0.555519f,0.553994f,0.552468f,0.550941f,0.549414f,0.547887f,0.546359f,0.544831f,
      0.543302f,0.541773f,0.540243f,0.538713f,0.537183f,0.535652f,0.534121f,0.532590f,0.531058f,0.529526f,0.527994f,
      0.526462f,0.524929f,0.523396f,0.521863f,0.520330f,0.518796f,0.517262f,0.515728f,0.514194f,0.512660f,0.511126f,
      0.509591f,0.508057f,0.506522f,0.504988f,0.503453f,0.501918f,0.500384f,0.498849f,0.497314f,0.495780f,0.494245f,
      0.492710f,0.491176f,0.489641f,0.488107f,0.486573f,0.485039f,0.483505f,0.481971f,0.480437f,0.478904f,0.477370f,
      0.475837f,0.474305f,0.472772f,0.471240f,0.469708f,0.468176f,0.466644f,0.465113f,0.463582f,0.462052f,0.460522f,
      0.458992f,0.457463f,0.455934f,0.454405f,0.452877f,0.451349f,0.449822f,0.448295f,0.446769f,0.445243f,0.443718f,
      0.442193f,0.440669f,0.439146f,0.437623f,0.436100f,0.434578f,0.433057f,0.431537f,0.430017f,0.428497f,0.426979f,
      0.425461f,0.423944f,0.422427f,0.420911f,0.419396f,0.417882f,0.416368f,0.414856f,0.413344f,0.411833f,0.410322f,
      0.408813f,0.407305f,0.405797f,0.404290f,0.402784f,0.401279f,0.399775f,0.398272f,0.396770f,0.395269f,0.393768f,
      0.392269f,0.390771f,0.389274f,0.387778f,0.386283f,0.384789f,0.383296f,0.381804f,0.380314f,0.378824f,0.377336f,
      0.375848f,0.374362f,0.372877f,0.371394f,0.369911f,0.368430f,0.366950f,0.365471f,0.363994f,0.362517f,0.361042f,
      0.359569f,0.358097f,0.356626f,0.355156f,0.353688f,0.352221f,0.350755f,0.349291f,0.347829f,0.346368f,0.344908f,
      0.343449f,0.341993f,0.340537f,0.339083f,0.337631f,0.336180f,0.334731f,0.333283f,0.331837f,0.330393f,0.328950f,
      0.327509f,0.326069f,0.324631f,0.323194f,0.321760f,0.320327f,0.318895f,0.317466f,0.316038f,0.314611f,0.313187f,
      0.311764f,0.310343f,0.308924f,0.307507f,0.306091f,0.304678f,0.303266f,0.301856f,0.300448f,0.299041f,0.297637f,
      0.296235f,0.294834f,0.293435f,0.292039f,0.290644f,0.289251f,0.287861f,0.286472f,0.285085f,0.283700f,0.282318f,
      0.280937f,0.279558f,0.278182f,0.276808f,0.275435f,0.274065f,0.272697f,0.271331f,0.269967f,0.268606f,0.267247f,
      0.265889f,0.264534f,0.263182f,0.261831f,0.260483f,0.259137f,0.257793f,0.256451f,0.255112f,0.253775f,0.252441f,
      0.251108f,0.249779f,0.248451f,0.247126f,0.245803f,0.244483f,0.243165f,0.241849f,0.240536f,0.239225f,0.237917f,
      0.236611f,0.235308f,0.234007f,0.232709f,0.231413f,0.230120f,0.228829f,0.227541f,0.226255f,0.224972f,0.223692f,
      0.222414f,0.221139f,0.219867f,0.218597f,0.217329f,0.216065f,0.214803f,0.213544f,0.212287f,0.211033f,0.209782f,
      0.208534f,0.207288f,0.206045f,0.204805f,0.203568f,0.202333f,0.201102f,0.199873f,0.198647f,0.197423f,0.196203f,
      0.194986f,0.193771f,0.192559f,0.191350f,0.190144f,0.188941f,0.187741f,0.186544f,0.185350f,0.184158f,0.182970f,
      0.181785f,0.180603f,0.179423f,0.178247f,0.177074f,0.175904f,0.174737f,0.173572f,0.172411f,0.171254f,0.170099f,
      0.168947f,0.167799f,0.166653f,0.165511f,0.164372f,0.163236f,0.162103f,0.160973f,0.159847f,0.158723f,0.157603f,
      0.156487f,0.155373f,0.154263f,0.153156f,0.152052f,0.150951f,0.149854f,0.148760f,0.147670f,0.146582f,0.145498f,
      0.144418f,0.143340f,0.142266f,0.141196f,0.140129f,0.139065f,0.138005f,0.136948f,0.135894f,0.134844f,0.133797f,
      0.132754f,0.131714f,0.130678f,0.129645f,0.128616f,0.127590f,0.126568f,0.125549f,0.124534f,0.123522f,0.122514f,
      0.121509f,0.120508f,0.119511f,0.118517f,0.117526f,0.116540f,0.115557f,0.114577f,0.113601f,0.112629f,0.111661f,
      0.110696f,0.109734f,0.108777f,0.107823f,0.106873f,0.105926f,0.104984f,0.104045f,0.103109f,0.102178f,0.101250f,
      0.100326f,0.099406f,0.098489f,0.097576f,0.096667f,0.095762f,0.094861f,0.093963f,0.093070f,0.092180f,0.091294f,
      0.090412f,0.089533f,0.088659f,0.087788f,0.086922f,0.086059f,0.085200f,0.084345f,0.083494f,0.082647f,0.081804f,
      0.080964f,0.080129f,0.079298f,0.078470f,0.077647f,0.076828f,0.076012f,0.075201f,0.074393f,0.073590f,0.072790f,
      0.071995f,0.071204f,0.070416f,0.069633f,0.068854f,0.068078f,0.067307f,0.066540f,0.065777f,0.065019f,0.064264f,
      0.063513f,0.062767f,0.062024f,0.061286f,0.060552f,0.059822f,0.059096f,0.058374f,0.057657f,0.056943f,0.056234f,
      0.055529f,0.054828f,0.054132f,0.053439f,0.052751f,0.052067f,0.051387f,0.050711f,0.050040f,0.049373f,0.048710f,
      0.048052f,0.047397f,0.046747f,0.046101f,0.045460f,0.044822f,0.044189f,0.043561f,0.042936f,0.042316f,0.041701f,
      0.041089f,0.040482f,0.039879f,0.039281f,0.038687f,0.038097f,0.037512f,0.036930f,0.036354f,0.035781f,0.035214f,
      0.034650f,0.034091f,0.033536f,0.032986f,0.032440f,0.031898f,0.031361f,0.030828f,0.030300f,0.029776f,0.029256f,
      0.028741f,0.028231f,0.027724f,0.027223f,0.026725f,0.026233f,0.025744f,0.025260f,0.024781f,0.024306f,0.023836f,
      0.023370f,0.022908f,0.022451f,0.021999f,0.021551f,0.021107f,0.020668f,0.020234f,0.019804f,0.019379f,0.018958f,
      0.018541f,0.018130f,0.017722f,0.017320f,0.016921f,0.016528f,0.016139f,0.015754f,0.015374f,0.014999f,0.014628f,
      0.014262f,0.013900f,0.013543f,0.013191f,0.012843f,0.012499f,0.012161f,0.011827f,0.011497f,0.011172f,0.010852f,
      0.010536f,0.010225f,0.009919f,0.009617f,0.009319f,0.009027f,0.008739f,0.008455f,0.008177f,0.007903f,0.007633f,
      0.007368f,0.007108f,0.006853f,0.006602f,0.006355f,0.006114f,0.005877f,0.005645f,0.005417f,0.005194f,0.004976f,
      0.004762f,0.004553f,0.004349f,0.004149f,0.003954f,0.003764f,0.003578f,0.003397f,0.003221f,0.003049f,0.002883f,
      0.002720f,0.002563f,0.002410f,0.002262f,0.002118f,0.001980f,0.001845f,0.001716f,0.001591f,0.001471f,0.001356f,
      0.001245f,0.001140f,0.001038f,0.000942f,0.000850f,0.000763f,0.000681f,0.000603f,0.000530f,0.000462f,0.000398f,
      0.000339f,0.000285f,0.000236f,0.000191f,0.000151f,0.000115f,0.000085f,0.000059f,0.000038f,0.000021f,0.000009f,
      0.000002f,0.000000f };

// -----------------------------------------------------------------------------

OptFFT::OptFFT(const size_t maxDataSize)
{
   assert( maxDataSize % OVERLAPSAMPLES == 0 );

   // DOUBLE
   //m_pIn = static_cast<double*>( fftw_malloc(sizeof(double) * FRAMESIZE) );
   //m_pOut = static_cast<fftw_complex*>( fftw_malloc(sizeof(fftw_complex) * (FRAMESIZE/2 + 1)) );
	//m_p = fftw_plan_dft_r2c_1f(FRAMESIZE, m_pIn, m_pOut, FFTW_ESTIMATE); // FFTW_ESTIMATE or FFTW_MEASURE

   // FLOAT
 //  m_pIn = static_cast<float*>( fftwf_malloc(sizeof(float) * FRAMESIZE) );
 //  m_pOut = static_cast<fftwf_complex*>( fftwf_malloc(sizeof(fftwf_complex) * (FRAMESIZE/2 + 1)) );

	//// in destroyed when line executed
	//m_p = fftwf_plan_dft_r2c_1d(FRAMESIZE, m_pIn, m_pOut, FFTW_ESTIMATE); // FFTW_ESTIMATE or FFTW_MEASURE

   //-----------------------------------------------------------------

   int numSamplesPerFrame    = FRAMESIZE;
   int numSamplesPerFrameOut = FRAMESIZE/2+1;

 	m_maxFrames = static_cast<int> ( (maxDataSize - FRAMESIZE) / OVERLAPSAMPLES + 1 );

   m_pIn  = static_cast<float*> ( fftwf_malloc(sizeof(float) * (numSamplesPerFrame * m_maxFrames) ) );
   if ( !m_pIn )
   {
      ostringstream oss;
      oss << "fftwf_malloc failed on m_pIn. Trying to allocate <" 
          << sizeof(float) * (numSamplesPerFrame * m_maxFrames)
          << "> bytes";
      throw std::runtime_error(oss.str());
   }

   m_pOut = static_cast<fftwf_complex*>( fftwf_malloc(sizeof(fftwf_complex) * (numSamplesPerFrameOut* m_maxFrames) ) );
   if ( !m_pOut )
   {
      ostringstream oss;
      oss << "fftwf_malloc failed on m_pOut. Trying to allocate <" 
          << sizeof(fftwf_complex) * (numSamplesPerFrameOut* m_maxFrames)
          << "> bytes";

      throw std::runtime_error(oss.str());
   }

	// in destroyed when line executed
   m_p = fftwf_plan_many_dft_r2c(1, &numSamplesPerFrame, m_maxFrames,
                                 m_pIn, &numSamplesPerFrame, 1, numSamplesPerFrame,
                                 m_pOut, &numSamplesPerFrameOut,
                                 1, numSamplesPerFrameOut,
                                 FFTW_ESTIMATE | FFTW_DESTROY_INPUT);

   if ( !m_p )
      throw std::runtime_error ("fftwf_plan_many_dft_r2c failed");

	double base = exp( log( static_cast<double>(MAXFREQ) / static_cast<double>(MINFREQ) ) / 
                      static_cast<double>(Filter::NBANDS) 
                     );

   m_powTable.resize( Filter::NBANDS+1 );
   for ( unsigned int i = 0; i < Filter::NBANDS + 1; ++i )
      m_powTable[i] = static_cast<unsigned int>( (pow(base, static_cast<double>(i)) - 1.0) * MINCOEF );

   m_pFrames = new float*[m_maxFrames];

   if ( !m_pFrames )
   {
      ostringstream oss;
      oss << "Allocation failed on m_pFrames. Trying to allocate <" 
         << sizeof(float*) * m_maxFrames
         << "> bytes";

      throw std::runtime_error(oss.str());
   }


   for (int i = 0; i < m_maxFrames; ++i) 
   {
      m_pFrames[i] = new float[Filter::NBANDS];
      if ( !m_pFrames[i] )
         throw std::runtime_error("Allocation failed on m_pFrames");
   }

}

// ----------------------------------------------------------------------

OptFFT::~OptFFT()
{
	fftwf_destroy_plan(m_p);
	
	fftwf_free(m_pIn);
	fftwf_free(m_pOut);

   for (int i = 0; i < m_maxFrames; ++i)
      delete [] m_pFrames[i];

   delete [] m_pFrames;
}

// ----------------------------------------------------------------------

int OptFFT::process(float* pInData, const size_t dataSize)
{
   // generally is the same of the one we used in the constructor (m_maxFrames) but
   // might be less at the end of the stream
   int nFrames = static_cast<int>( (dataSize - FRAMESIZE) / OVERLAPSAMPLES + 1 );

   float* pIn_It = m_pIn;

   for (int i = 0; i < nFrames; ++i)
   {
      memcpy( pIn_It, &pInData[i*OVERLAPSAMPLES], sizeof(float) * FRAMESIZE);
      // apply hanning window
      applyHann(pIn_It, FRAMESIZE);

      pIn_It += FRAMESIZE;
   }

   // fill the rest with zeroes
   if ( nFrames < m_maxFrames )
      memset( pIn_It, 0, sizeof(float) * (m_maxFrames-nFrames) * FRAMESIZE );

   fftwf_execute(m_p);

   int totSamples = (FRAMESIZE/2+1) * // numSamplesPerFrameOut
                    nFrames; // the frames actually in the input

   // scaling (?)
   float scalingFactor = static_cast<float>(FRAMESIZE) / 2.0f;
   for (int k = 0; k < totSamples; ++k)
   {
      m_pOut[k][0] /= scalingFactor;
      m_pOut[k][1] /= scalingFactor;
   }

   int frameStart;
   unsigned int outBlocStart;
   unsigned int outBlocEnd;

	for (int i = 0; i < nFrames; ++i) 
   {
      frameStart = i * (FRAMESIZE/2+1);

	   // compute bands
	   for (unsigned int j = 0; j < Filter::NBANDS; j++) 
      {
         outBlocStart = m_powTable[j] + frameStart;
         outBlocEnd   = m_powTable[j+1] + frameStart;

		   m_pFrames[i][j] = 0;

		   // WARNING: We're double counting the last one here.
		   // this bug is to match matlab's implementation bug in power2band.m
         unsigned int end_k = outBlocEnd + static_cast<unsigned int>(MINCOEF);
		   for (unsigned int k = outBlocStart + static_cast<unsigned int>(MINCOEF); k <= end_k; k++) 
         {
			   m_pFrames[i][j] += m_pOut[k][0] * m_pOut[k][0] + 
                               m_pOut[k][1] * m_pOut[k][1];
		   }

		   // WARNING: if we change the k<=end to k<end above, we need to change the following line
		   m_pFrames[i][j] /= static_cast<float>(outBlocEnd - outBlocStart + 1);   		
	   }   
   }

   return nFrames;
}

// -----------------------------------------------------------------------------

void OptFFT::applyHann( float* pInData, const size_t dataSize )
{
   assert (dataSize == 2048);

   for ( size_t i = 0; i < dataSize; ++i )
      pInData[i] *= hann[i];
}

// -----------------------------------------------------------------------------

} // end of namespace

// ----------------------------------------------------------------------
