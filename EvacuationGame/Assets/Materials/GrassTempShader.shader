Shader "Custom/SmoothTriplanarGround"
{
    Properties
    {
        _ColorA("Color A", Color) = (0.23,0.18,0.11,1)
        _ColorB("Color B", Color) = (0.41,0.36,0.23,1)
        _Scale("Texture Scale", Float) = 0.1
        _SlopeDark("Slope Darkening", Float) = 0.5
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 worldPos : TEXCOORD0;
                float3 worldNormal : TEXCOORD1;
            };

            fixed4 _ColorA;
            fixed4 _ColorB;
            float _Scale;
            float _SlopeDark;

            // Classic Perlin-like noise
            float noise(float2 uv)
            {
                return frac(sin(dot(uv, float2(12.9898, 78.233))) * 43758.5453);
            }

            float smoothNoise(float2 uv)
            {
                float2 i = floor(uv);
                float2 f = frac(uv);

                float a = noise(i);
                float b = noise(i + float2(1,0));
                float c = noise(i + float2(0,1));
                float d = noise(i + float2(1,1));

                float2 u = f*f*(3.0-2.0*f);
                return lerp(lerp(a,b,u.x), lerp(c,d,u.x), u.y);
            }

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                o.worldNormal = normalize(mul((float3x3)unity_ObjectToWorld, v.normal));
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float3 n = abs(normalize(i.worldNormal));

                float3 scalePos = i.worldPos * _Scale;

                float2 uvX = scalePos.yz;
                float2 uvY = scalePos.xz;
                float2 uvZ = scalePos.xy;

                float nx = n.x;
                float ny = n.y;
                float nz = n.z;

                float fx = smoothNoise(uvX);
                float fy = smoothNoise(uvY);
                float fz = smoothNoise(uvZ);

                float3 colorX = lerp(_ColorA.rgb, _ColorB.rgb, fx);
                float3 colorY = lerp(_ColorA.rgb, _ColorB.rgb, fy);
                float3 colorZ = lerp(_ColorA.rgb, _ColorB.rgb, fz);

                float3 blended = colorX*nx + colorY*ny + colorZ*nz;
                blended /= (nx + ny + nz + 0.0001);

                // Darken steep slopes
                float slopeFactor = lerp(1.0, _SlopeDark, 1.0 - n.y);
                blended *= slopeFactor;

                return float4(blended,1);
            }
            ENDCG
        }
    }
}
