uniform sampler2D texture;

void main()
{
    vec2 uv = gl_TexCoord[0].xy;

    vec4 pixel = texture2D(texture, uv);

    if (pixel.a == 0.0)
    {
        discard;
    }

    gl_FragColor = vec4(1.0, 1.0, 1.0, pixel.a);
}
