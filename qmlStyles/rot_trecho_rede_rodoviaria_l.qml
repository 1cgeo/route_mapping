<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Forms" version="3.14.16-Pi">
  <renderer-v2 type="RuleRenderer" symbollevels="0" forceraster="0" enableorderby="0">
    <rules key="{f64af78d-ceb2-48a1-bde4-3a42e686fed4}">
      <rule symbol="0" key="{36d15a7e-f728-40df-9bcc-13de4e3d026d}" filter=" is_selected( )"/>
      <rule symbol="1" key="{548b275b-03dd-4ab7-a867-b2dc1f02d5d6}" filter=" &quot;bidirecional&quot;  IS TRUE"/>
      <rule symbol="2" key="{ad7e3d53-0e00-4083-9b2c-3f3881d84f5a}" filter=" &quot;bidirecional&quot;  IS FALSE"/>
    </rules>
    <symbols>
      <symbol type="line" name="0" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" locked="0" pass="0" class="GeometryGenerator">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="with_variable('restriction',&#xd;&#xa;string_to_array(&#xd;&#xa;aggregate(&#xd;&#xa; layer:= 'rot_restricao',&#xd;&#xa; aggregate:='concatenate',&#xd;&#xa; expression:= to_string( &quot;id_2&quot;),&#xd;&#xa; concatenator:=',',&#xd;&#xa; filter:=attribute(@parent,'id') = &quot;id_1&quot;&#xd;&#xa;),&#xd;&#xa;','&#xd;&#xa;)&#xd;&#xa;,&#xd;&#xa;&#xd;&#xa;with_variable('ponto',&#xd;&#xa;if(&quot;bidirecional&quot;,collect_geometries(start_point($geometry),end_point($geometry)),end_point($geometry))&#xd;&#xa;,&#xd;&#xa;&#xd;&#xa;with_variable('ponto_buffer',&#xd;&#xa;buffer(@ponto, 0.0005)&#xd;&#xa;,&#xd;&#xa;&#xd;&#xa;collect_geometries(&#xd;&#xa;array_foreach(&#xd;&#xa;array_filter(&#xd;&#xa;string_to_array(&#xd;&#xa;aggregate(&#xd;&#xa; layer:= 'rot_trecho_rede_rodoviaria_l',&#xd;&#xa; aggregate:='concatenate',&#xd;&#xa; expression:= to_string( &quot;id&quot;),&#xd;&#xa; concatenator:=',',&#xd;&#xa; filter:= intersects($geometry, @ponto) and attribute(@parent,'id') != &quot;id&quot; and (&quot;bidirecional&quot; or intersects(start_point($geometry), @ponto))&#xd;&#xa;),&#xd;&#xa;','&#xd;&#xa;),&#xd;&#xa;not array_contains( @restriction, @element))&#xd;&#xa;,&#xd;&#xa;with_variable('linha',&#xd;&#xa;intersection(geometry(get_feature('rot_trecho_rede_rodoviaria_l', 'id', to_int(@element))), @ponto_buffer),&#xd;&#xa;if(intersects(start_point(@linha), @ponto), @linha, reverse(@linha))&#xd;&#xa;)&#xd;&#xa;&#xd;&#xa;)&#xd;&#xa;)&#xd;&#xa;)&#xd;&#xa;)&#xd;&#xa;)"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" name="@0@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <layer enabled="1" locked="0" pass="0" class="ArrowLine">
              <prop k="arrow_start_width" v="3"/>
              <prop k="arrow_start_width_unit" v="MM"/>
              <prop k="arrow_start_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="arrow_type" v="0"/>
              <prop k="arrow_width" v="3"/>
              <prop k="arrow_width_unit" v="MM"/>
              <prop k="arrow_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_length" v="8"/>
              <prop k="head_length_unit" v="MM"/>
              <prop k="head_length_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_thickness" v="5"/>
              <prop k="head_thickness_unit" v="MM"/>
              <prop k="head_thickness_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_type" v="0"/>
              <prop k="is_curved" v="1"/>
              <prop k="is_repeated" v="0"/>
              <prop k="offset" v="5.55112e-17"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="ring_filter" v="0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="fill" name="@@0@0@0" alpha="1" clip_to_extent="1" force_rhr="0">
                <layer enabled="1" locked="0" pass="0" class="SimpleFill">
                  <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="254,0,97,255"/>
                  <prop k="joinstyle" v="round"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="0,0,0,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="1"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="style" v="solid"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" name="1" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" locked="0" pass="0" class="SimpleLine">
          <prop k="capstyle" v="square"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="line_color" v="219,30,42,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.66"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="line" name="2" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" locked="0" pass="0" class="SimpleLine">
          <prop k="capstyle" v="square"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="line_color" v="179,1,255,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.8"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer enabled="1" locked="0" pass="0" class="MarkerLine">
          <prop k="average_angle_length" v="0"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="30"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="centralpoint"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="marker" name="@2@1" alpha="1" clip_to_extent="1" force_rhr="0">
            <layer enabled="1" locked="0" pass="0" class="SimpleMarker">
              <prop k="angle" v="90"/>
              <prop k="color" v="179,1,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="triangle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.4"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="5"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="acostamento"/>
    <field editable="1" name="administracao"/>
    <field editable="1" name="alturamaxima"/>
    <field editable="1" name="bidirecional"/>
    <field editable="1" name="canteirodivisorio"/>
    <field editable="1" name="codtrechorod"/>
    <field editable="1" name="concessionaria"/>
    <field editable="1" name="geometriaaproximada"/>
    <field editable="1" name="id"/>
    <field editable="1" name="jurisdicao"/>
    <field editable="1" name="larguramaxima"/>
    <field editable="0" name="lenght_otf"/>
    <field editable="1" name="limitevelocidade"/>
    <field editable="1" name="limitevelocidadeveiculospesados"/>
    <field editable="1" name="nome"/>
    <field editable="1" name="nrfaixas"/>
    <field editable="1" name="nrpistas"/>
    <field editable="1" name="observacao"/>
    <field editable="1" name="operacional"/>
    <field editable="1" name="proibidocaminhoes"/>
    <field editable="1" name="revestimento"/>
    <field editable="1" name="sigla"/>
    <field editable="1" name="situacaofisica"/>
    <field editable="1" name="tipopavimentacao"/>
    <field editable="1" name="tipovia"/>
    <field editable="1" name="tonelagemmaxima"/>
    <field editable="1" name="trafego"/>
    <field editable="1" name="trechoemperimetrourbano"/>
  </editable>
  <labelOnTop>
    <field name="acostamento" labelOnTop="0"/>
    <field name="administracao" labelOnTop="0"/>
    <field name="alturamaxima" labelOnTop="0"/>
    <field name="bidirecional" labelOnTop="0"/>
    <field name="canteirodivisorio" labelOnTop="0"/>
    <field name="codtrechorod" labelOnTop="0"/>
    <field name="concessionaria" labelOnTop="0"/>
    <field name="geometriaaproximada" labelOnTop="0"/>
    <field name="id" labelOnTop="0"/>
    <field name="jurisdicao" labelOnTop="0"/>
    <field name="larguramaxima" labelOnTop="0"/>
    <field name="lenght_otf" labelOnTop="0"/>
    <field name="limitevelocidade" labelOnTop="0"/>
    <field name="limitevelocidadeveiculospesados" labelOnTop="0"/>
    <field name="nome" labelOnTop="0"/>
    <field name="nrfaixas" labelOnTop="0"/>
    <field name="nrpistas" labelOnTop="0"/>
    <field name="observacao" labelOnTop="0"/>
    <field name="operacional" labelOnTop="0"/>
    <field name="proibidocaminhoes" labelOnTop="0"/>
    <field name="revestimento" labelOnTop="0"/>
    <field name="sigla" labelOnTop="0"/>
    <field name="situacaofisica" labelOnTop="0"/>
    <field name="tipopavimentacao" labelOnTop="0"/>
    <field name="tipovia" labelOnTop="0"/>
    <field name="tonelagemmaxima" labelOnTop="0"/>
    <field name="trafego" labelOnTop="0"/>
    <field name="trechoemperimetrourbano" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
