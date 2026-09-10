uniform sampler2D texture;
uniform float progress;

float random(vec2 st)
{
    return fract(
        sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123
    );
}

void main()
{
    vec2 uv = gl_TexCoord[0].xy;

    // Divide sprite into particle cells
    vec2 cell = floor(uv * 18.0);

    float noise = random(cell);

    // Particles fall downward as the dissolve progresses
    float fallAmount = progress * 0.35;

    vec2 particleUV = uv;

    particleUV.y -= fallAmount;

    // Keep the particle movement slightly different
    // for each particle
    particleUV.y -= random(cell + 5.0) * progress * 0.15;

    vec4 pixel = texture2D(texture, particleUV);

    // Particles disappear at different times
    if (noise < progress)
    {
        discard;
    }

    gl_FragColor = pixel;
}
