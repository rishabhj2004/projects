uniform sampler2D texture;
uniform sampler2D noiseTex; 
uniform float time;
uniform vec2 tilePos; 
uniform vec4 borders; 
uniform vec4 uvBounds; // x=left, y=top, z=right, w=bottom

void main()
{
    vec2 uv = gl_TexCoord[0].xy;
    vec2 globalPos = tilePos + (uv * 32.0); 

    // Random Sway Controls
    float noiseScale   = 0.3;    
    float swaySpeed    = 1.0;      
    float maxMovement  = 0.002; 

    vec2 timeOffset = vec2(sin(time * swaySpeed), cos(time * swaySpeed * 1.2)) * 0.1;
    vec2 noiseUV    = (globalPos * noiseScale) + timeOffset;
    vec2 noiseOffset = (texture2D(noiseTex, noiseUV).xy - 0.5) * 2.0;

    float exposed = step(0.0, max(max(borders.x, borders.y), max(borders.z, borders.w)));

    vec2 offset = noiseOffset * maxMovement * exposed;
    
    //Prevents Texture Bleeding
    vec2 finalUV = clamp(uv + offset, uvBounds.xy, uvBounds.zw);

    gl_FragColor = gl_Color * texture2D(texture, finalUV);
}
